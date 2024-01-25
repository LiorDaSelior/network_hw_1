import numbers_service as ns
import socket as sk
import sys
from typing import Dict, Set

HOST = "127.0.0.1"
PORT = 1337

# incoming_msg_dict : Dict[sk.socket, ns.IncomingSocketMessage] = {} # dict to administer all incoming messages
# outgoing_msg_dict : Dict[sk.socket, ns.OutgoingSocketMessage] = {} # dict to administer all outgoing messages

# def send_msg(target_socket: sk.socket, msg: str):
#         sk_msg = ns.OutgoingSocketMessage(msg)
#         outgoing_msg_dict[target_socket] = sk_msg
#         target_socket.send(sk_msg.size)
        
# def recv_msg(source_socket: sk.socket, size_in_bytes: bytes):
#         size = int.from_bytes(size_in_bytes, "big") # ! TODO - mention "big" ordering on lsb
#         sk_msg = ns.IncomingSocketMessage(size)
#         incoming_msg_dict[source_socket] = sk_msg

logged_in_flag = False

with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as cilent_socket:
    cilent_socket.connect((HOST, PORT))
    data = cilent_socket.recv(1024)
    print(int.from_bytes(data, "big"))
    data = cilent_socket.recv(1024)
    print(data.decode(encoding = "utf-8"))
    while True:
        if logged_in_flag:
            input()
        else:

            
            user_cred = input()
            user_cred += "\n" + input()
            data = f"{user_cred}".encode(encoding = "utf-8")
            cilent_socket.send(len(data).to_bytes(4, 'big'))
            cilent_socket.send(data)
            
            data = cilent_socket.recv(1024)
            print(int.from_bytes(data, "big"))
            data = cilent_socket.recv(1024)
            msg = data.decode(encoding = "utf-8")
            print(msg)
            if "Hi" in msg:
                logged_in_flag = True
            
    