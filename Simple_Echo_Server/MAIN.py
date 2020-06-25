from socket import *                                                        # Use socket API
import sys                                                                  # Access system operations

from SERVER import Server                                                   # Import server and client classes
from CLIENT import Client

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print ('Usage: python myprog.py c <address> <port> or python myprog.py s <port>')
    elif sys.argv[1] != "s" and sys.argv[1]!="c":
        print ('Usage: python myprog.py c <address> <port> or python myprog.py s <port>')
    elif sys.argv[1] == "s":
        server = Server(int(sys.argv[2]))
        server.run()
    else:
        client = Client(sys.argv[2], int(sys.argv[3]))
        client.run()