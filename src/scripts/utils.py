import sys, os
import socket
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from algorithm.rsa import RSA
from algorithm.utils import UserInterfaceUtils

HOST = "127.0.0.1"
PORT = 8000
BUFFER_SIZE = 50000
IS_COMMUNICATION_MODE = True

class CommunicationUtils:
    @staticmethod
    def create_server_socket():
        server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))
        server.listen(5)
        return server
    
    @staticmethod
    def create_client_socket():
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        return client
    
    @staticmethod 
    def send_pulic_key(connection, rsa):
        connection.send(str(rsa.params.n).encode("utf8"))
        connection.send(str(rsa.params.d).encode("utf8"))
    
    @staticmethod
    def receive_public_key(client):
        n = int(client.recv(BUFFER_SIZE).decode("utf8"))
        d = int(client.recv(BUFFER_SIZE).decode("utf8"))
        return n, d
    
    @staticmethod
    def send_encrypted_messages(connection: socket, rsa:RSA, message):
        if message == "":
            connection.send(str(0).encode("utf8"))
            UserInterfaceUtils.display_termination_message("Sender")
            sys.exit(0)
        else:
            connection.send(str(len(message)).encode("utf8"))
        RSA.send_encrypted_message_blocks(connection, message, rsa.params.e, rsa.params.n, rsa.key_length, IS_COMMUNICATION_MODE)

    @staticmethod
    def decrypt_received_messages(client, n, d):
        message_length = int(client.recv(BUFFER_SIZE).decode("utf8"))
        if message_length == 0:
            UserInterfaceUtils.display_termination_message("Receiver")
            sys.exit(0)
        message = ""
        while message_length != 0:
            block_tuples = client.recv(BUFFER_SIZE).decode("utf8").split("\n")[0:-1]
            for block_tuple in block_tuples:
                block = int(block_tuple.split("\t")[0])
                block_size = int(block_tuple.split("\t")[1])
                decrypted_block = RSA.decrypt_message_block(block, block_size, d, n)
                message += decrypted_block
                message_length -= (block_size/8)
        print(message)