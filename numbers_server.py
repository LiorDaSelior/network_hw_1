import numbers_service as ns
import select as sl
import socket as sk
import sys

#! TODO - What is protocol
#! TODO - Errors

HOST = ""
DEFAULT_PORT = 1337

def get_user_info(user_data_filename):
    res = {}
    with open(user_data_filename, 'r', encoding="utf-8") as user_data_file:
        for row in user_data_file.read().splitlines():
            row_iter = row.split('\t')
            res[row_iter[0]] = row_iter[1]
    return res

user_data_filename = ""
port = ""
waiting_socket_set = set()
connected_socket_set = set()

if len(sys.argv) == 2:
    user_data_filename = sys.argv[1]
    port = DEFAULT_PORT
elif  len(sys.argv) == 3:
    user_data_filename = sys.argv[1]
    port = int(sys.argv[2])
else:
    raise AttributeError("Command line arguments are invalid")

listener_socket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
listener_socket.bind((HOST, port))
listener_socket.listen() #? is there a limit
socket_list = [listener_socket]
while True:
    readable, _, _ = sl.select(socket_list, [], [])
    
    for socket in readable:
        if socket == listener_socket:
            connect_socket, addr = listener_socket.accept()
            socket_list.append(connect_socket)
            waiting_socket_set.add(connect_socket)
            welcome_msg = "Welcome! Please log in."
            connect_socket.send(welcome_msg.encode("utf-8"))
            
        elif socket in waiting_socket_set:
            data = socket.recv(1024)
            message = data.decode(encoding = "utf-8")
            user_cred = message.split(" ") #! TODO - Redefine login protocol
            user = user_cred[0]
            password = user_cred[1]
            user_data = get_user_info(user_data_filename)
            if user in user_data and user_data[user] == password:
                waiting_socket_set.remove(socket)
                connected_socket_set.add(socket)
                login_msg = f"Hi {user}, good to see you."
                connect_socket.send(login_msg.encode("utf-8"))
            else:
                fail_msg = "Failed to login."
                connect_socket.send(fail_msg.encode("utf-8"))
            
        elif socket in connected_socket_set:
            data = socket.recv(1024)
            cmd = data.decode(encoding = "utf-8")
            cmd_arr = cmd.split(":")
            cmd_name = cmd_arr[0]
            
            if cmd == "quit" or cmd_name not in ns.command_list:
                connected_socket_set.remove(socket)
                socket_list.remove(socket)
                socket.close()
            else:
                #try:
                cmd_args = ((cmd_arr[1])[1:]).split(" ")
                connect_socket.send(ns.execute(cmd_name, cmd_args).encode("utf-8"))
                #except (ns.InvalidCommandArgumentException, ValueError):
                #    connected_socket_set.remove(socket)
                #    socket_list.remove(socket)
                #    socket.close()
                
            