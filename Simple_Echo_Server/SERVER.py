from socket import *                                                               # Import the python socket API
import sys                                                                         # Import sys commands


class Server:

    # Constructor - Specifies port number property
    def __init__(self, port_number):
        self.server_ip = ''
        self.port_number = port_number

    # Sets up communication network between server and client
    def run(self):
        # Step 1 - Create server socket
        try:
            server_socket = socket(AF_INET, SOCK_STREAM, 0)
        except error as errorMessage:
            print(f"Socket could not be created : {str(errorMessage)}")           # Print error if socket could not be created

        # Step 2 - Bind the socket to the network
        server_socket.bind((self.server_ip, self.port_number))
        server_socket.listen(5)

        connection, addressInfo = server_socket.accept()                          # Unpack output of accepting a connection from client

        # Set up a new connection from the client
        while True:
            print('The server is ready to receive')
            # Server should be up and running and listening to the incoming connections
            receivedInformation = connection.recv(512)
            if not receivedInformation:
                connection.close()
                break

            connection.sendall(receivedInformation)

        server_socket.close()
        sys.exit()                                                                      # Terminate the program after sending the corresponding data
