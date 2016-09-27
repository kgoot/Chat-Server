import socket
import sys
import time

class BasicServer(object):

    def __init__(self, port):
        self.port = port
        self.server_socket = socket.socket()
        self.server_socket.bind(("0.0.0.0", int(port)))
        self.server_socket.listen(5)
        while True:
            #needs to use select here so that its non blocking -- look in the link lmao
            print("entered the while")
            #this creates a new socket to deal with the new client
            (clientsocket, address) = self.server_socket.accept()
            data = clientsocket.recv(200) #recieve takes in number of bytes not chars?!
            #we strip the data of like whitespace at the end
            #we will analyze it #start calling helpers to do whatever
            print(data)

            print("Got a connection from %s" % str(address))

            clientsocket.close()

args = sys.argv
if len(args) != 2:
    print "Something's wrong woot."
    sys.exit()
client = BasicServer(args[1])


#Unlike your server in part 0, your server in this part of 
#the assignment must allow many clients to be connected 
#and sending messages concurrently. Each client should have 
#an associated name (so that other connected clients know who 
#each message is from) and channel that they're currently subscribed to.
# When a client first connects, it won't have an associated name and channel.
# The first message that the server receives from the client should be used 
#as the client's name.