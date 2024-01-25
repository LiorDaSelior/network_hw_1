import numbers_service as ns
import select as sl
import socket as sk
import sys
from typing import Dict, Set

#! TODO - What is protocol
#! TODO - Errors

HOST = ""
DEFAULT_PORT = 1337
DATA_BANDWIDTH = 4

user_data_filename : str = ""
port : int = DEFAULT_PORT
logging_socket_set : Set[sk.socket] = set() # set to administer all sockets which init. login
connected_socket_set : Set[sk.socket] = set() # set to administer all sockets which completed login
disconnected_socket_set : Set[sk.socket] = set() # set to administer all sockets which exited server and are receiving final message
incoming_msg_dict : Dict[sk.socket, ns.IncomingSocketMessage] = {} # dict to administer all incoming messages
outgoing_msg_dict : Dict[sk.socket, ns.OutgoingSocketMessage] = {} # dict to administer all outgoing messages

if len(sys.argv) == 2:
    user_data_filename = sys.argv[1]
    port = DEFAULT_PORT
elif  len(sys.argv) == 3:
    user_data_filename = sys.argv[1]
    port = int(sys.argv[2])
else:
    raise AttributeError("Server set up failed - Arguments are invalid")

#try:
listener_socket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
listener_socket.bind((HOST, port))
listener_socket.listen() #? is there a limit - dont care
#except: - #! TODO - Check for errors during socket creation
readable_socket_list = [listener_socket]
writable_socket_list = []


# shorthand func
def send_msg(target_socket: sk.socket, msg: str): # Send str msg to socket - add msg to data struct and begin sending buffer. Socket must be writable
    sk_msg = ns.OutgoingSocketMessage(msg)
    outgoing_msg_dict[target_socket] = sk_msg
    target_socket.send(sk_msg.size.to_bytes(4, 'big'))
        
def recv_msg(source_socket: sk.socket): # Get str msg from socket - add msg to data struct and begin receiving buffer. Return False <=> recv size is 0. Socket must be readable
    size_in_bytes = socket.recv(4)
    size = int.from_bytes(size_in_bytes, "big")
    if size == 0:
        return False
    sk_msg = ns.IncomingSocketMessage(size)
    incoming_msg_dict[source_socket] = sk_msg
    return True


while True:
    readable, writable, _ = sl.select(readable_socket_list, writable_socket_list, [], 10)
    
    for socket in readable: 
        if socket in incoming_msg_dict: # if currently receiving buffered message from the socket -> add received data to data struct
            if not incoming_msg_dict[socket].is_complete():
                incoming_msg_dict[socket].add_data(socket.recv(DATA_BANDWIDTH))
        
        if socket == listener_socket: # init. connection
            connect_socket, addr = listener_socket.accept()
            logging_socket_set.add(connect_socket) # init. login process. Turn socket to writable to send welcome msg
            writable_socket_list.append(connect_socket) 
            send_msg(connect_socket, "Welcome! Please log in.")
            
        elif socket in logging_socket_set:
            if socket in incoming_msg_dict:
                if incoming_msg_dict[socket].is_complete(): # if server received all 'logging details' bytes -> get msg content as string for login analysis
                    login_cred = (incoming_msg_dict[socket].data).decode()
                    incoming_msg_dict.pop(socket) # after extracting the msg content, remove msg from data struct. Now we expect to write response to socket, therefore we turn it from readable to writable
                    readable_socket_list.remove(socket)
                    writable_socket_list.append(socket) 
                    res = ns.login(login_cred, ns.get_user_info(user_data_filename)) # extract login credentials and execute login process
                    if res is None: # res = None <=> login format is wrong. Disconnect socket - send final msg and remove from all relevant data struct (After writing the msg, socket won't be readable, cause it's added to disconnected_socket_set)
                        logging_socket_set.remove(socket)
                        disconnected_socket_set.add(socket)
                        send_msg(socket, "Error - Disconnected from server.")                  
                    elif res == True: # res = True <=> login format is right, username and password are matching. Add user to connected_socket_set
                        user_name = ns.get_cred(login_cred)[0]
                        logging_socket_set.remove(socket)
                        connected_socket_set.add(socket)
                        send_msg(socket, f"Hi {user_name}, good to see you.")
                    else: # res = False <=> login format is right, username OR password are wrong. Wait for another attempt
                        send_msg(socket, "Login Failed.")
                    
            else: # if server didn't recognize incoming msg from from socket <=> expects socket to send size of 'logging details' data
                if not recv_msg(socket): # if False -> response size is 0, therefore disconnect socket
                    logging_socket_set.remove(socket)
                    disconnected_socket_set.add(socket)
                    writable_socket_list.append(socket) 
                    send_msg(socket, "Error - Disconnected from server.")
    for socket in writable:
        if socket in outgoing_msg_dict: # if server sends socket buffered messages -> continue sending remaining data
            socket.send(outgoing_msg_dict[socket].get_data(DATA_BANDWIDTH))
            if outgoing_msg_dict[socket].is_complete(): # if msg is fully sent -> delete from data struct. Remove socket from writable
                outgoing_msg_dict.pop(socket)
                writable_socket_list.remove(socket)
                if socket in disconnected_socket_set: # if socket is not disconnected -> server expects to receive data from socket after writing to it, therefore turn socket readable
                    disconnected_socket_set.remove(socket)
                    socket.close()
                else:
                    readable_socket_list.append(socket)

                    