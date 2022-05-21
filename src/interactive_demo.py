import sys, getopt
import socket
from algorithm.rsa import RSA
from algorithm.utils import UserInterfaceUtils

IS_INTERACTIVE = True
HOST = "127.0.0.1"
PORT = 8000
BUFFER_SIZE = 5000

def print_help_message():
    print("use one of the following options:\n\t-h (for help)\n\t-t sender (to send)\n\t-t receiver (to receive)")
    sys.exit(2)

def send_encrypted_messages(connection, rsa):
    while True:
        message = UserInterfaceUtils.get_message_from_user()
        connection.send(str(len(message)).encode("utf8"))
        for character in range(0, len(message)):
            encrypted_chars = RSA.encrypt_character(message[character], rsa.params.e, rsa.params.n)
            connection.send((str(encrypted_chars) + "\n").encode("utf8"))
        if message == "":
            connection.send(str(0).encode("utf8"))
            UserInterfaceUtils.display_termination_message("Sender")
            break

def decrypt_received_messages(client, n, d):
    while True:
        message_length = int(client.recv(BUFFER_SIZE).decode("utf8"))
        if message_length == 0:
            UserInterfaceUtils.display_termination_message("Receiver")
            break
        message = ""
        while message_length != 0:
            encrypted_chars = client.recv(BUFFER_SIZE).decode("utf8").split("\n")[0:-1]
            for encrypted_char in encrypted_chars:
                decrypted_char = RSA.decrypt_character(int(encrypted_char), d, n)
                message += decrypted_char
                message_length -= 1
        print(message)

def create_server_socket():
    server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    return server

def execute_sender_behavior():
    server = create_server_socket()
    UserInterfaceUtils.display_waiting_message("Sender")
    connection, _ = server.accept()
    rsa = RSA()
    rsa.generate_key(IS_INTERACTIVE)
    connection.send(str(rsa.params.n).encode("utf8"))
    connection.send(str(rsa.params.d).encode("utf8"))
    send_encrypted_messages(connection, rsa)

def execute_receiver_behavior():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    UserInterfaceUtils.display_waiting_message("Receiver")
    n = int(client.recv(BUFFER_SIZE).decode("utf8"))
    d = int(client.recv(BUFFER_SIZE).decode("utf8"))
    decrypt_received_messages(client, n, d)

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