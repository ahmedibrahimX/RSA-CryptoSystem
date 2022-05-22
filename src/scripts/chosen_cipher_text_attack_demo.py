import sys, os
import random
import threading
from string import ascii_letters, digits
from time import sleep

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from algorithm.rsa import RSA
from algorithm.utils import RSAUtils, UserInterfaceUtils
from scripts.utils import CommunicationUtils

IS_NOT_INTERACTIVE = False
lock = threading.Condition()

def generate_random_message(length_in_bits):
    message = ""
    while (len(message.encode("utf8")) * 8) < length_in_bits:
        message += str(random.choice(ascii_letters + digits))
    return message

def execute_legitimate_behavior():
    legitimate_user = CommunicationUtils.create_server_socket()
    rsa = RSA()
    rsa.generate_key(IS_NOT_INTERACTIVE)
    connection, _ = legitimate_user.accept()
    CommunicationUtils.send_pulic_key(connection, rsa)
    message1 = generate_random_message(rsa.key_length - 8)
    CommunicationUtils.send_encrypted_messages(connection, rsa, message1)
    received_message = int(connection.recv(CommunicationUtils.BUFFER_SIZE).decode("utf8"))
    received_message_decrypted = pow(received_message, rsa.params.d, rsa.params.n)
    connection.send(str(received_message_decrypted).encode("utf8"))



def execute_attacker_behavior():
    attacker = CommunicationUtils.create_client_socket()
    n, e =CommunicationUtils.receive_public_key(attacker)
    attacker.recv(CommunicationUtils.BUFFER_SIZE).decode("utf8")
    message1_tuple = attacker.recv(CommunicationUtils.BUFFER_SIZE).decode("utf8").split("\n")[0:-1]
    message1_encrypted = int(message1_tuple.split("\t")[0])
    message1_len = int(message1_tuple.split("\t")[1])
    r = random.choice(range(2, rsa.n))
    manipulated_message = (message1_encrypted * pow(r, rsa.params.e, rsa.params.n)) % rsa.params.n
    attacker.send(str(manipulated_message).encode("utf8"))
    message2 = int(attacker.recv(CommunicationUtils.BUFFER_SIZE).decode("utf8"))
    r_inverse = RSAUtils.get_inverse(r, rsa.params.n)
    message1_decrypted = (message2 * r_inverse) % rsa.params.n
    message1_str = ""
    for i in range(message1_len):
        message1_str = message1_decrypted[i] + message1_str
    print(message1_str)

def main():
    Bob = threading.Thread(target=execute_legitimate_behavior)
    
    Eve = threading.Thread(target=execute_attacker_behavior)

    Bob.start()
    sleep(3)
    Eve.start()

    Bob.join()
    Eve.join()

if __name__ == '__main__':
    main()