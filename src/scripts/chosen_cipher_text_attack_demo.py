import sys, os
import random
import threading
import math
from string import ascii_letters, digits
from time import sleep

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from algorithm.rsa import RSA
from algorithm.utils import RSAUtils
from scripts.utils import CommunicationUtils

IS_NOT_INTERACTIVE = False

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
    CommunicationUtils.send_public_key(connection, rsa)
    original_message = generate_random_message((rsa.key_length - 8) * random.choice(range(1, 11)))
    print("Original message at legitimate user side:\n", original_message, "\n")
    CommunicationUtils.send_encrypted_messages(connection, rsa.params.e, rsa.params.n, rsa.key_length, original_message)
    CommunicationUtils.resend_back_corrupt_messages(rsa, connection)

def trick_victim_into_decrypting_chosen_chipertext(attacker, n, e, encrypted_block, r):
    chosen_ciphertext_block = (encrypted_block * pow(r, e, n)) % n
    attacker.send(str(chosen_ciphertext_block).encode("utf8"))
    chosen_chiphertext_block_decrypted = int(attacker.recv(CommunicationUtils.BUFFER_SIZE).decode("utf8"))
    return chosen_chiphertext_block_decrypted

def extract_original_block(n, inverse_of_random_factor, chosen_chiphertext_block_decrypted):
    original_block_decrypted_chars = (chosen_chiphertext_block_decrypted * inverse_of_random_factor) % n
    return original_block_decrypted_chars

def reorder_characters_into_original_format(message_length, encrypted_block_length, original_block_decrypted_chars):
    original_block_decrypted_str = ""
    num_processed_bits = 0
    while num_processed_bits < encrypted_block_length:
        character = chr(original_block_decrypted_chars & 0xFF)
        original_block_decrypted_chars = original_block_decrypted_chars >> 8
        original_block_decrypted_str = character + original_block_decrypted_str
        num_processed_bits += 8
        message_length -= 1
    return original_block_decrypted_str

def execute_attacker_behavior():
    attacker = CommunicationUtils.create_client_socket()
    n, e =CommunicationUtils.receive_public_key(attacker)
    message_length = int(attacker.recv(CommunicationUtils.BUFFER_SIZE).decode("utf8"))
    block_tuples = CommunicationUtils.receive_all_blocks_at_once(attacker, message_length)
    decrypted_message = ""
    for block_tuple in block_tuples:
        encrypted_block = int(block_tuple.split("\t")[0])
        encrypted_block_length = int(block_tuple.split("\t")[1])
        
        random_factor = random.choice(range(2, n if n < 100 else 100))
        inverse_of_random_factor = RSAUtils.get_inverse(random_factor, n)
        
        chosen_chiphertext_block_decrypted = trick_victim_into_decrypting_chosen_chipertext(attacker, n, e, encrypted_block, random_factor)
        original_block_decrypted_chars = extract_original_block(n, inverse_of_random_factor, chosen_chiphertext_block_decrypted)
        original_block_decrypted_str = reorder_characters_into_original_format(message_length, encrypted_block_length, original_block_decrypted_chars)
        
        decrypted_message += original_block_decrypted_str
    print("Decrypted message at attacker side:\n", decrypted_message, "\n")
    attacker.send(str(0).encode("utf8"))

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