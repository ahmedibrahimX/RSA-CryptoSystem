import sys, os
import random
import math
import multiprocessing
from time import sleep
import matplotlib.pyplot as plt
import datetime
import yaml
from progressbar import *
from string import ascii_letters, digits
from matplotlib.offsetbox import AnchoredText

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from algorithm.utils import RSAUtils
from algorithm.rsa import RSA

IS_NOT_INTERACTIVE = False
IS_BRUTEFORCE_ATTACK_MODE = False
KEY_CONFIG = 0
PRIME_CONGFIG=1

def search_for_prime_factor(start, end, n, factors_found, p_q):
    widgets = ['Bruteforcing factors: ', Percentage(), ' ', Bar(marker='0',left='[',right=']'),
        ' ', ETA(), ' ', FileTransferSpeed(unit="key")]
    pbar = ProgressBar(widgets=widgets, maxval=end-start+1)
    progress = 0
    pbar.start()
    p = start
    while p <= end and p * p < n and factors_found.is_set() == False:
        # if RSAUtils.is_probably_a_prime(p) and RSAUtils.is_miller_rabin_strong_prime(p) and n % p == 0:
        #NOTE: No need to check if it's a prime or not as n will only have 2 factors which are p and q (based on prime factorization theorem)
        if n % p == 0:
            q = n // p
            p_q["values"] = (p, q)
            pbar.finish()
            factors_found.set()
            break
        else:
            progress += 1
            pbar.update(progress)
            p += 1
    pbar.finish()

def bruteforce_factorization(n):
    global value
    if n % 2 == 0:
        return 2, n//2
    manager = multiprocessing.Manager()
    factors_found = manager.Event()
    upper_limit = math.ceil(math.sqrt(n))
    step = math.ceil((upper_limit-2) / 10)
    processes = []
    p_q = manager.dict()
    start = 3
    while start <  upper_limit:
        end = start + step if (start + 2 * step) < upper_limit else upper_limit
        process = multiprocessing.Process(target=search_for_prime_factor, args=(start, end, n, factors_found, p_q))
        start = end+1
        processes.append(process)
        process.start()
    factors_found.wait()
    for process in processes:
        process.terminate()
    return p_q["values"][0], p_q["values"][1]



def generate_random_message(length_in_bits):
    message = ""
    while (len(message.encode("utf8")) * 8) < length_in_bits:
        message += str(random.choice(ascii_letters + digits))
    return message

def set_configurations(key_len, prime_min_length):
    with open(os.path.join(os.path.dirname(__file__), "../configurations.yaml")) as f:
        doc = yaml.full_load(f)
    doc['KEY_GENERATION']['KEY_LENGTH'] = key_len
    doc['KEY_GENERATION']['PRIME_MIN_LENGTH'] = prime_min_length
    with open(os.path.join(os.path.dirname(__file__), "../configurations.yaml"), 'w') as f:
        yaml.dump(doc, f)

def get_attack_iterations_count():
    with open(os.path.join(os.path.dirname(__file__), "../configurations.yaml"), "r") as f:
            config = yaml.safe_load(f)
    count = config["ATTACK_ITERATIONS_COUNT"]
    assert count > 0, "attack iterations count should be >= 1"
    print("number of iterations is : " + str(count))
    return count

def plot_bruteforce_stats_vs_keysize(attack_time_avg, key_lens):
    plt.style.use('ggplot')
    fig, ax = plt.subplots()
    plt.grid(True)
    ax.plot(key_lens, attack_time_avg, marker="o", markersize=5)
    ax.set_title("Bruteforce Time vs Key Length Stats")
    ax.set_xlabel("Key length in bits")
    ax.set_ylabel("Time in seconds")
    plt.savefig(os.path.join(os.path.dirname(__file__), "..") + '/stats/bruteforce_stats/bruteforce_time_vs_keysize_stats.png', bbox_inches='tight')
    plt.show()

def annotate_n_value(ax, n, time):
    ax.annotate(
    str(n),
    xy=(n, time), xycoords='data',
    xytext=(5, 0), textcoords='offset points',
    size=7,
    bbox=dict(boxstyle="round4,pad=.5", fc="0.8", alpha=0.4),
    arrowprops=dict(arrowstyle="-"))

def plot_bruteforce_stats_vs_n_value(n_vs_time):
    plt.style.use('ggplot')
    fig, ax = plt.subplots()
    plt.grid(True)
    n_vals = [coord[0] for coord in n_vs_time]
    time = [coord[1] for coord in n_vs_time]
    ax.scatter(n_vals, time, marker="o")
    for coord in n_vs_time:
        annotate_n_value(ax, coord[0], coord[1])
    ax.set_title("Bruteforce Time vs n Value Stats")
    ax.set_xlabel("n value")
    ax.set_ylabel("Time in seconds")
    ax.add_artist(AnchoredText('annotations on points represent n values', loc=2))
    plt.savefig(os.path.join(os.path.dirname(__file__), "..") + '/stats/bruteforce_stats/bruteforce_time_vs_nvalue_stats.png', bbox_inches='tight')
    plt.show()

def main():
    key_len__prime_min_len = [(8, 2), (16, 7), (32, 15), (40, 19)]
    n_vs_time = []
    attack_time_avg = [0,0,0,0]

    iterations_count = int(get_attack_iterations_count())
    for _ in range(0, iterations_count):
        test_case_num = 0
        for configs in key_len__prime_min_len:
            set_configurations(configs[KEY_CONFIG], configs[PRIME_CONGFIG])
            rsa = RSA()

            rsa.generate_key(IS_NOT_INTERACTIVE)
            original_message = generate_random_message(rsa.key_length-8)
            encrypted_block_tuples = RSA.send_encrypted_message_blocks(None, original_message, rsa.params.e, rsa.params.n, rsa.key_length, IS_BRUTEFORCE_ATTACK_MODE)

            attack_start = datetime.datetime.now()
            p, q = bruteforce_factorization(rsa.params.n)
            phi = (p - 1) * (q - 1)
            d = RSAUtils.get_inverse(rsa.params.e, phi)
            attack_finish = datetime.datetime.now()
            
            decrypted_message = ""
            for tuple in encrypted_block_tuples:
                block = int(tuple.decode("utf8").strip("\n").split("\t")[0])
                block_size = int(tuple.decode("utf8").strip("\n").split("\t")[1])
                decrypted_block = RSA.decrypt_message_block(block, block_size, d, rsa.params.n)
                decrypted_message += decrypted_block
            assert decrypted_message == original_message, "decryption doesn't match original message"

            attack_time_avg[test_case_num] += (attack_finish - attack_start).total_seconds() / float(iterations_count)
            n_vs_time.append((rsa.params.n, (attack_finish - attack_start).total_seconds()))
            test_case_num += 1
    print(attack_time_avg)
    key_lens = [config[KEY_CONFIG] for config in key_len__prime_min_len]
    plot_bruteforce_stats_vs_keysize(attack_time_avg, key_lens)
    plot_bruteforce_stats_vs_n_value(n_vs_time)


if __name__ == "__main__":
    main()