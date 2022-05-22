import sys, os
import random
import yaml
import datetime
from string import ascii_letters, digits
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from algorithm.rsa import RSA

IS_NOT_INTERACTIVE = False
KEY_CONFIG = 0
PRIME_CONGFIG=1
MSG_CONFIG=2
IS_STATISTICS_MODE = False

def generate_random_message(length_in_bits):
    message = ""
    while (len(message.encode("utf8")) * 8) < length_in_bits:
        message += str(random.choice(ascii_letters + digits))
    return message

def set_configurations(key_length, prime_min_length):
    with open(os.path.join(os.path.dirname(__file__), "../configurations.yaml")) as f:
        doc = yaml.full_load(f)
    doc['KEY_GENERATION']['KEY_LENGTH'] = key_length
    doc['KEY_GENERATION']['PRIME_MIN_LENGTH'] = prime_min_length
    with open(os.path.join(os.path.dirname(__file__), "../configurations.yaml"), 'w') as f:
        yaml.dump(doc, f)

def get_stats_iterations_count():
    with open(os.path.join(os.path.dirname(__file__), "../configurations.yaml"), "r") as f:
            config = yaml.safe_load(f)
    count = config["STATS_ITERATIONS_COUNT"]
    assert count > 0, "stats iterations count should be >= 1"
    print("number of iterations is : " + str(count))
    return count

def plot_key_gen_stats(key_generation_time_avg, key_lens):
    plt.style.use('ggplot')
    fig, ax = plt.subplots()
    plt.grid(True)
    ax.plot(key_lens, key_generation_time_avg, marker="o", markersize=5)
    ax.set_title("Key Generation Stats")
    ax.set_xlabel("Key length in bits")
    ax.set_ylabel("Time in seconds")
    plt.savefig(os.path.join(os.path.dirname(__file__), "..") + '/stats/rsa_stats/key_generation_stats.png', bbox_inches='tight')
    plt.show()

def annotate_msg_size(ax, size, x, y, point_index):
    ax.annotate(
    str(size),
    xy=(x, y), xycoords='data',
    xytext=(-5*point_index, point_index * (3 if point_index % 2 == 1 else -5)), textcoords='offset points',
    size=7,
    bbox=dict(boxstyle="round4,pad=.5", fc="0.8", alpha=0.4),
    arrowprops=dict(arrowstyle="->", color="black",
                    connectionstyle="angle,angleA=0,angleB=-90,rad=10"))

def plot_ecnryption_stats(encryption_time_avg, key_lens, msg_sizes):
    plt.style.use('ggplot')
    fig, ax = plt.subplots(figsize=(25, 6))
    plt.grid(True)
    ax.plot(key_lens, encryption_time_avg, marker="o", markersize=5)
    ax.set_title("Encryption Stats")
    ax.set_xlabel("Key length in bits")
    ax.set_ylabel("Time in seconds")
    ax.add_artist(AnchoredText('annotations on points represent message sizes in bits', loc=2))
    for i in range(len(key_lens)):
        annotate_msg_size(ax, msg_sizes[i], key_lens[i], encryption_time_avg[i], i)
    plt.savefig(os.path.join(os.path.dirname(__file__), "..") + '/stats/rsa_stats/encryption_stats.png', bbox_inches='tight')
    plt.show()

def plot_total_rsa_stats(total_rsa_time_avg, key_lens, msg_sizes):
    plt.style.use('ggplot')
    fig, ax = plt.subplots(figsize=(25, 6))
    plt.grid(True)
    ax.plot(key_lens, total_rsa_time_avg, marker="o", markersize=5)
    ax.set_title("Total RSA Stats")
    ax.set_xlabel("Key length in bits")
    ax.set_ylabel("Time in seconds")
    ax.add_artist(AnchoredText('annotations on points represent message sizes in bits', loc=2))
    for i in range(len(key_lens)):
        annotate_msg_size(ax, msg_sizes[i], key_lens[i], total_rsa_time_avg[i], i)
    plt.savefig(os.path.join(os.path.dirname(__file__), "..") + '/stats/rsa_stats/total_rsa_stats.png', bbox_inches='tight')
    plt.show()

def main():
    key_len__prime_min_len__msg_len = [(32, 8, 20), (40, 10, 20), (56, 15, 20),
    (64, 30, 40), (128, 60, 40), (256, 120, 40), 
    (512, 250, 300), (1024, 500, 300), (2048, 1000, 300)]
    key_generation_time_avg = [0,0,0,0,0,0,0,0,0]
    encryption_time_avg = [0,0,0,0,0,0,0,0,0]
    total_rsa_time_avg = [0,0,0,0,0,0,0,0,0]
    key_lens = [config[KEY_CONFIG] for config in key_len__prime_min_len__msg_len]
    msg_sizes = [config[MSG_CONFIG] for config in key_len__prime_min_len__msg_len]

    iterations_count = int(get_stats_iterations_count())
    for _ in range(0, iterations_count):
        test_case_num = 0
        for configs in key_len__prime_min_len__msg_len:
            set_configurations(configs[KEY_CONFIG], configs[PRIME_CONGFIG])
            rsa = RSA()
            
            key_generation_start = datetime.datetime.now()
            rsa.generate_key(IS_NOT_INTERACTIVE)
            key_generation_finish = datetime.datetime.now()
            
            message = generate_random_message(configs[MSG_CONFIG])
            
            encryption_start = datetime.datetime.now()
            RSA.send_encrypted_message_blocks(None, message, rsa.params.e, rsa.params.n, configs[KEY_CONFIG], IS_STATISTICS_MODE)
            encryption_finish = datetime.datetime.now()
            
            key_generation_time = (key_generation_finish - key_generation_start).total_seconds()
            key_generation_time_avg[test_case_num] += key_generation_time / float(iterations_count)

            encryption_time = (encryption_finish - encryption_start).total_seconds()
            encryption_time_avg[test_case_num] += encryption_time / float(iterations_count)
            
            total_rsa_time_avg[test_case_num] += (key_generation_time + encryption_time) / float(iterations_count)
            test_case_num += 1
    
    plot_key_gen_stats(key_generation_time_avg, key_lens)
    plot_ecnryption_stats(encryption_time_avg, key_lens, msg_sizes)
    plot_total_rsa_stats(total_rsa_time_avg, key_lens, msg_sizes)


if __name__ == "__main__":
    main()
