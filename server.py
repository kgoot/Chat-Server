import socket
import sys
import select
import utils

class Server(object):

    def __init__(self, port):
        self.socket_list = []
        self.socket_to_name = {}
        self.socket_to_channel = {}
        self.channels = {}
        self.messages = {}
        self.port = port
        self.server_socket = socket.socket()
        self.server_socket.bind(("0.0.0.0", int(port)))
        self.server_socket.listen(10)
        self.socket_list.append(self.server_socket)
        while True:
            ready_to_read, ready_to_write, in_error = select.select(self.socket_list, [], [])
            for sock in ready_to_read:
                if self.server_socket == sock: #new connection request
                    clientsocket, address = self.server_socket.accept()
                    self.socket_list.append(clientsocket)
                    
                    name = clientsocket.recv(utils.MESSAGE_LENGTH)
                    if len(name) < utils.MESSAGE_LENGTH:
                        self.messages[clientsocket] = name
                    else:
                        self.socket_to_name[clientsocket] = name.rstrip()    
                else: # a message from a client, not a new connection
                    try:
                        output = self.process_buffer(sock)
                        print(output)
                        if output:
                            data = output.rstrip()
                            print(data)
                            if sock in self.messages.keys():
                                self.socket_to_name[sock] = name.rstrip()
                            if data[0] == '/': #special message
                                if data.split(' ', 1)[0] == '/join':
                                    if data == '/join':
                                        self.broadcast(sock, [sock], utils.SERVER_JOIN_REQUIRES_ARGUMENT)
                                    else:
                                        self.join(sock, data)
                                elif data.split(' ', 1)[0] == '/create':
                                    if data == '/create':
                                        self.broadcast(sock, [sock], utils.SERVER_CREATE_REQUIRES_ARGUMENT)
                                    else:
                                        self.create(sock, data)
                                elif data.split(' ', 1)[0] == '/list':
                                    self.list(sock)
                                else:
                                    self.broadcast(
                                        sock,
                                        [sock],
                                        utils.SERVER_INVALID_CONTROL_MESSAGE.format(data.split(' ', 1)[0]))
                            else: #regular message
                                if sock not in self.socket_to_channel.keys():
                                    self.broadcast(sock, [sock], utils.SERVER_CLIENT_NOT_IN_CHANNEL)
                                else:
                                    client_name = self.socket_to_name[sock]
                                    channel_to_broadcast = self.socket_to_channel[sock]
                                    self.broadcast(sock, [s for s in self.channels[channel_to_broadcast] if s != sock], "[" + client_name + "] " + data.strip())

                    except:
                        if sock in self.socket_list:
                            self.socket_list.remove(sock)
                        if sock in self.socket_to_channel.keys():
                            self.channels[self.socket_to_channel[sock]] = [s for s in self.channels[self.socket_to_channel[sock]] if s != sock]
                            self.broadcast(
                                sock, 
                                self.channels[self.socket_to_channel[sock]],
                                utils.SERVER_CLIENT_LEFT_CHANNEL.format(self.socket_to_name[sock]))
                            del self.socket_to_channel[sock]
                        continue
        server_socket.close()


    def join(self, sock, data):
        channel_name = data[6:]
        if channel_name not in self.channels.keys():
            self.broadcast(sock, [sock], utils.SERVER_NO_CHANNEL_EXISTS.format(channel_name))
        else:
            self.remove_from_channels(sock)
            self.channels[channel_name] += [sock]
            self.socket_to_channel[sock] = channel_name            
            self.broadcast(
                sock,
                [s for s in self.channels[channel_name] if s != sock],
                utils.SERVER_CLIENT_JOINED_CHANNEL.format(self.socket_to_name[sock]))
         
    def remove_from_channels(self, sock):
        for channel_name in self.channels.keys():
            if sock in self.channels[channel_name]:
                self.channels[channel_name].remove(sock)
                del self.socket_to_channel[sock]
                if self.channels[channel_name]:
                    self.broadcast(
                        sock,
                        self.channels[channel_name],
                        utils.SERVER_CLIENT_LEFT_CHANNEL.format(self.socket_to_name[sock]))

    def create(self, sock, data):
        channel_name = data[8:]
        if channel_name in self.channels.keys():
            self.broadcast(sock, [sock], utils.SERVER_CHANNEL_EXISTS.format(channel_name))
        else:
            self.remove_from_channels(sock)
            self.channels[channel_name] = [sock]
            self.socket_to_channel[sock] = channel_name
       
    def list(self, sock):
        if self.channels.keys():
            available_channels = '\n'.join(self.channels.keys())
            self.broadcast(sock, [sock], available_channels)

    def broadcast(self, sender, destination_list, message):
        for sock in destination_list:
            try:
                sock.send(message.ljust(utils.MESSAGE_LENGTH))
            except:
                # broken socket connection
                sock.close()
                # broken socket, remove it
                if sock in self.socket_list:
                    self.socket_list.remove(sock)

    def process_buffer(self, sock):
        output = None
        recieved_message = sock.recv(utils.MESSAGE_LENGTH)
        if not recieved_message:
            self.broadcast(
                sock, 
                self.channels[self.socket_to_channel[sock]],
                utils.SERVER_CLIENT_LEFT_CHANNEL.format(self.socket_to_name[sock]))
        elif sock in self.messages.keys():
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
if len(args) != 2:
    print("Please supply a port.")
    sys.exit()
server = Server(args[1])
