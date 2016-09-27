import socket
import sys
import select
import utils

class Client(object):

    def __init__(self, name, address, port):
        self.name = name
        self.address = address
        self.messages = {}
        self.port = int(port)
        self.socket = socket.socket()
        try:
            self.socket.connect((self.address, self.port))
        except:
            sys.stdout.write(utils.CLIENT_CANNOT_CONNECT.format(self.address, self.port))
            sys.exit()
        
        self.socket.send(name.ljust(utils.MESSAGE_LENGTH))
        sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
        sys.stdout.flush() 

        while True:
            socket_list = [sys.stdin, self.socket]
            read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
             
            for sock in read_sockets:            
                if sock == self.socket: # Incoming message from remote server
                    output = self.process_buffer(sock)
                    data = output.rstrip()
                    sys.stdout.write(utils.CLIENT_WIPE_ME)
                    sys.stdout.write('\r' + data)
                    sys.stdout.write('\n' + utils.CLIENT_MESSAGE_PREFIX)
                    sys.stdout.flush()     
                
                else: # User entered a message
                    msg = sys.stdin.readline()
                    self.socket.send(msg.ljust(utils.MESSAGE_LENGTH))
                    sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
                    sys.stdout.flush() 

    def process_buffer(self, sock):
        output = None
        recieved_message = sock.recv(utils.MESSAGE_LENGTH)
        if not recieved_message:
            sys.stdout.write(utils.CLIENT_SERVER_DISCONNECTED.format(self.address, self.port))
            sys.exit()
        if sock in self.messages.keys():
            new_data = self.messages[sock] + recieved_message
            if len(new_data) >= utils.MESSAGE_LENGTH:
                output = new_data[:utils.MESSAGE_LENGTH]
                self.messages[sock] = new_data[utils.MESSAGE_LENGTH:]
            else:
                self.messages[sock] = new_data
        else:
            if len(recieved_message) == utils.MESSAGE_LENGTH:
                output = recieved_message
            else:
                self.messages[sock] = recieved_message
        return output

args = sys.argv
if len(args) != 4:
    print("Please supply a client name, server address and port.")
    sys.exit()
client = Client(args[1], args[2], args[3])
