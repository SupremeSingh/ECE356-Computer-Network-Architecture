from socket import *
import sys


class Client:

    # Constructor - Specifies host address and port number
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port

    def run(self):
        # Create server socket
        client_socket = socket(AF_INET, SOCK_STREAM, 0)

        # Add your code here
        client_socket.connect((self.server_ip, self.server_port))

        # Get input with python raw_input() or input()
        try:
            from_client = input("Enter message: \n")
        except EOFError:
            from_client = "bye"

        while from_client.lower().strip() != 'bye':
            # send and receive message
            client_socket.send(str.encode(from_client))

            from_server = repr(client_socket.recv(512))
            print(from_server)  # show in terminal

            # Get input again
            try:
                from_client = input("Enter message: \n")
            except EOFError:
                from_client = "bye"

        client_socket.close()  # close the connection
