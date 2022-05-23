import sys, os, getopt
import socket
import yaml
import math

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from algorithm.rsa import RSA
from algorithm.utils import UserInterfaceUtils
from scripts.utils import CommunicationUtils

IS_INTERACTIVE = True
BUFFER_SIZE = 50000

def print_help_message():
    print("use one of the following options:\n\t-h (for help)\n\t-t sender (to send)\n\t-t receiver (to receive)")
    sys.exit(2)

def execute_receiver_behavior():
    server = CommunicationUtils.create_server_socket()
    UserInterfaceUtils.display_waiting_message("Receiver")
    connection, _ = server.accept()
    rsa = RSA()
    rsa.generate_key(IS_INTERACTIVE)
    CommunicationUtils.send_public_key(connection, rsa)
    UserInterfaceUtils.display_key_sending_success()
    while True:
        CommunicationUtils.decrypt_received_messages(connection, rsa.params.n, rsa.params.d)

def execute_sender_behavior():
    with open(os.path.join(os.path.dirname(__file__), "../configurations.yaml"), "r") as f:
            config = yaml.safe_load(f)
    key_length = math.floor(config["KEY_GENERATION"]["KEY_LENGTH"])
    client = CommunicationUtils.create_client_socket()
    UserInterfaceUtils.display_waiting_message("Sender")
    n, e = CommunicationUtils.receive_public_key(client)
    UserInterfaceUtils.display_key_receiving_success()
    while True:
        message = UserInterfaceUtils.get_message_from_user()
        CommunicationUtils.send_encrypted_messages(client, e, n, key_length, message)
    

def main(argv):
    try:
        opts, _ = getopt.getopt(argv, "ht:")
    except getopt.GetoptError:
        print_help_message()
    if opts[0][0] == "-h":
        print_help_message()
    elif opts[0][0] == "-t":
        if opts[0][1] == "sender":
            execute_sender_behavior()
        elif opts[0][1] == "receiver":
            execute_receiver_behavior()
        else:
            print_help_message()

if __name__ == "__main__":
   main(sys.argv[1:])