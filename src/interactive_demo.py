import sys, getopt
import socket
from algorithm.rsa import RSA

IS_INTERACTIVE = True
HOST = "127.0.0.1"
PORT = 8000
BUFFER_SIZE = 5000

def print_help_message():
    print("use one of the following options:\n\t-h (for help)\n\t-t sender (to send)\n\t-t receiver (to receive)")
    sys.exit(2)

def main(argv):
    try:
        opts, _ = getopt.getopt(argv, "ht:")
    except getopt.GetoptError:
        print_help_message()
    if opts[0][0] == "-h":
        print_help_message()
    elif opts[0][0] == "-t":
        if opts[0][1] == "sender":
            server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((HOST, PORT))
            server.listen(5)
            print("sender listening for connections")
            connection, _ = server.accept()
            print(connection)
            rsa = RSA()
            rsa.generate_key(IS_INTERACTIVE)
            connection.send(str(rsa.params.n).encode('utf8'))
            connection.send(str(rsa.params.d).encode('utf8'))
        elif opts[0][1] == "receiver":
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST, PORT))
            print("receiver is waiting for key")
            n = int(client.recv(BUFFER_SIZE).decode('utf8'))
            d = int(client.recv(BUFFER_SIZE).decode('utf8'))
            print("d: " + str(d))
            print("=" * 60)
            print("n: " + str(n))
        else:
            print_help_message()

if __name__ == "__main__":
   main(sys.argv[1:])