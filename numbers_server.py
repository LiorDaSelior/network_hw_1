#!/usr/bin/python3

import numbers_service as ns
import select as sl
import socket as sk
import sys
import errno
from typing import Dict, Set

HOST = ""
DEFAULT_PORT = 1337
DATA_BANDWIDTH = 4

user_data_filename : str = ""
port : int = DEFAULT_PORT
logging_socket_set : Set[sk.socket] = set() # set for handling all sockets which init. login
connected_socket_set : Set[sk.socket] = set() # set for handling all sockets which completed login
disconnected_socket_set : Set[sk.socket] = set() # set for handling all sockets which disconnected from server, are receiving final message and closing
incoming_msg_dict : Dict[sk.socket, ns.IncomingSocketMessage] = {} # dict for handling all incoming messages
outgoing_msg_dict : Dict[sk.socket, ns.OutgoingSocketMessage] = {} # dict for handling all outgoing messages

if len(sys.argv) == 2:
    user_data_filename = sys.argv[1]
    port = DEFAULT_PORT
elif  len(sys.argv) == 3:
    user_data_filename = sys.argv[1]
    port = int(sys.argv[2])
else:
    raise AttributeError("Server setup failed - Arguments are invalid.")

listener_socket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)

try:
    listener_socket.bind((HOST, port))
    listener_socket.listen()
except OSError as exception:
    print(exception.strerror)
    print("Server setup failed - Error during listening socket setup.")
    exit()

readable_socket_list = [listener_socket]
writable_socket_list = []

# shorthand functions for repeating methods
def handle_socket_error(target_socket: sk.socket): # close socket and remove it from all relevant data structures
    if target_socket in readable_socket_list:
        readable_socket_list.remove(target_socket)
    if target_socket in writable_socket_list:
        writable_socket_list.remove(target_socket) 
    if target_socket in logging_socket_set:
        logging_socket_set.remove(target_socket) 
    if target_socket in connected_socket_set:
        connected_socket_set.remove(target_socket) 
    if target_socket in disconnected_socket_set:
        disconnected_socket_set.remove(target_socket) 
    if target_socket in incoming_msg_dict:
        incoming_msg_dict.pop(target_socket)
    if target_socket in outgoing_msg_dict:
        outgoing_msg_dict.pop(target_socket)
    target_socket.close()


def send_msg(target_socket: sk.socket, msg: str): # send str msg to socket - add msg to data struct and begin sending buffer. Turns socket from readable to writable
    if target_socket in readable_socket_list:
        readable_socket_list.remove(target_socket)
    if target_socket not in writable_socket_list:
        writable_socket_list.append(target_socket) 
    sk_msg = ns.OutgoingSocketMessage(msg)
    outgoing_msg_dict[target_socket] = sk_msg
    try:
        target_socket.send(sk_msg.size.to_bytes(4, 'big'))
    except OSError as exception:
        handle_socket_error(target_socket)
        if exception.errno == errno.ECONNRESET:
            pass
        else:
            print(exception.strerror)
        
def recv_msg(source_socket: sk.socket): # get str msg from socket - add msg to data struct and begin receiving buffer. Return False <=> recv size is 0. Socket must be readable
    size = 0
    try:
        size_in_bytes = source_socket.recv(4)
        size = int.from_bytes(size_in_bytes, "big")
    except OSError as exception:
        handle_socket_error(source_socket)
        if exception.errno == errno.ECONNRESET:
            pass
        else:
            print(exception.strerror)
        return True

    if size == 0:
        return False
    sk_msg = ns.IncomingSocketMessage(size)
    incoming_msg_dict[source_socket] = sk_msg
    return True

def disconnect_socket(target_socket: sk.socket, msg: str = "Disconnected from server."): # send "Disconnected" msg to socket - add socket to data struct for "Disconnected sockets" to send final msg and close connection after fully sending msg
    disconnected_socket_set.add(target_socket)
    send_msg(target_socket, msg)

while True:
    readable, writable, _ = sl.select(readable_socket_list, writable_socket_list, [], 10)
    
    for socket in readable: 
        if socket in incoming_msg_dict: # if currently receiving buffered message from the socket -> add received data to data struct
            if not incoming_msg_dict[socket].is_complete():
                try:
                    incoming_msg_dict[socket].add_data(socket.recv(DATA_BANDWIDTH))
                except OSError as exception:
                    handle_socket_error(socket)
                    if exception.errno == errno.ECONNRESET:
                        pass
                    else:
                        print(exception.strerror)
                    
        if socket == listener_socket: # init. connection
            error_flag = False
            try:
                connect_socket, addr = listener_socket.accept()
            except OSError as exception:
                print(exception.strerror)
                error_flag = True
            if not error_flag:
                logging_socket_set.add(connect_socket) # init. login process.
                send_msg(connect_socket, "Welcome! Please log in.")
            
        elif socket in logging_socket_set: # if socket in login process -> recv login credentials data
            if socket in incoming_msg_dict:
                if incoming_msg_dict[socket].is_complete(): # if server received all 'logging details' bytes -> get msg content as string for login analysis
                    login_cred = (incoming_msg_dict[socket].data).decode()
                    incoming_msg_dict.pop(socket) # after extracting the msg content, remove msg from data struct. Now we expect to write response to socket 
                    res = ns.login(login_cred, ns.get_user_info(user_data_filename)) # extract login credentials and execute login process
                    if res is None: # res = None <=> login format is wrong. Disconnect socket - send final msg and remove from all relevant data struct (After writing the msg, socket won't be readable, cause it's added to disconnected_socket_set)
                        logging_socket_set.remove(socket)
                        disconnect_socket(socket)                
                    elif res == True: # res = True <=> login format is right, username and password are matching. Add user to connected_socket_set
                        user_name = ns.get_cred(login_cred)[0]
                        logging_socket_set.remove(socket)
                        connected_socket_set.add(socket)
                        send_msg(socket, f"Hi {user_name}, good to see you.")
                    else: # res = False <=> login format is right, username OR password are wrong. Wait for another attempt
                        send_msg(socket, "Login Failed.")
                    
            else: # if server didn't recognize existing incoming msg in data struct from from socket -> start recv msg from socket
                if not recv_msg(socket): # if False -> response size is 0. Therefore disconnect socket
                    logging_socket_set.remove(socket)
                    disconnect_socket(socket)
                    
        elif socket in connected_socket_set:
            if socket in incoming_msg_dict:
                if incoming_msg_dict[socket].is_complete():
                    cmd = (incoming_msg_dict[socket].data).decode()
                    incoming_msg_dict.pop(socket)
                    res = ns.execute(cmd)
                    if res is None: # res = None <=> command is not recognized OR is quit, disconnect user
                        connected_socket_set.remove(socket)
                        disconnect_socket(socket)
                    else:
                        send_msg(socket, "response: " + res + ".")
                    
            else:
                if not recv_msg(socket):
                    connected_socket_set.remove(socket)
                    disconnect_socket(socket)
    
    for socket in writable:
        if socket in outgoing_msg_dict: # if server started sending the socket buffered messages -> continue sending the remaining msg data
            try:
                socket.send(outgoing_msg_dict[socket].get_data(DATA_BANDWIDTH))
            except OSError as exception:
                handle_socket_error(socket)
                if exception.errno == errno.ECONNRESET:
                    pass
                else:
                    print(exception.strerror)
                    
            if socket in outgoing_msg_dict and outgoing_msg_dict[socket].is_complete(): # if msg is fully sent -> delete from data struct. Remove socket from writable. (We check again if socket in outgoing_msg_dict in case of Connection Error)
                outgoing_msg_dict.pop(socket)
                writable_socket_list.remove(socket)
                if socket in disconnected_socket_set: # if socket is not disconnected -> server expects to receive data from socket after writing to it, therefore turn socket readable
                    disconnected_socket_set.remove(socket)
                    socket.close()
                else:
                    readable_socket_list.append(socket)

                    