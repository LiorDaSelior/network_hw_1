import numbers_service as ns
import socket as sk
import sys

HOST = "127.0.0.1"
PORT = 1337

logged_in_flag = False

with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as cilent_socket:
    cilent_socket.connect((HOST, PORT))
    data = cilent_socket.recv(1024)
    print(data.decode(encoding = "utf-8"))
    while not logged_in_flag:
        user = input("Enter username: ") #! TODO - Redefine login protocol
        password = input("Enter password: ")
        cilent_socket.send(f"{user} {password}".encode(encoding = "utf-8"))
        data = cilent_socket.recv(1024)
        msg = data.decode(encoding = "utf-8")
        print(msg)
        logged_in_flag = msg.find("Hi") != -1
    while True:
        cmd = input()
        
        cmd_arr = cmd.split(":")
        cmd_name = cmd_arr[0]
        cmd_args = ((cmd_arr[1])[1:]).split(" ")
        if cmd != "quit" and not ns.check_cmd_arguments(cmd_name, cmd_args):
            cmd = "quit"
            print("An error has occurred.")
        
        cilent_socket.send(cmd.encode(encoding = "utf-8"))
        if cmd == "quit":
            print("Connection closed.")
            break
        else:
            data = cilent_socket.recv(1024)
            if len(data) == 0:
                print("Connection closed.")
                break
            else:
                msg = data.decode(encoding = "utf-8")
                print(f"response: {msg}.")
            
    