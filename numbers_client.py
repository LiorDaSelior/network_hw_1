import numbers_service as ns
import socket as sk
import sys

HOST = "127.0.0.1"
PORT = 1337
DATA_BANDWIDTH = 4

current_msg = None
logged_in_flag = False

with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as cilent_socket:
    cilent_socket.connect((HOST, PORT))
    size_in_bytes = cilent_socket.recv(4)
    size = int.from_bytes(size_in_bytes, "big")
    current_msg = ns.IncomingSocketMessage(size)
    while not current_msg.is_complete():
        current_msg.add_data(cilent_socket.recv(DATA_BANDWIDTH))
    print(current_msg.data.decode(encoding = "utf-8")) # welcome msg
    
    while not logged_in_flag:
        
        # login attempt
        first_line_input = input() 
        second_line_input = input()
        current_msg = ns.OutgoingSocketMessage(f"{first_line_input}\n{second_line_input}")
        cilent_socket.send(current_msg.size.to_bytes(4, 'big')) # send size
        while not current_msg.is_complete(): # sending login cred
            cilent_socket.send(current_msg.get_data(DATA_BANDWIDTH))
            
        # recv server response to login
        size_in_bytes = cilent_socket.recv(4) 
        size = int.from_bytes(size_in_bytes, "big")
        current_msg = ns.IncomingSocketMessage(size)
        while not current_msg.is_complete():
            current_msg.add_data(cilent_socket.recv(DATA_BANDWIDTH))
        res = current_msg.data.decode(encoding = "utf-8") # login msg
        print(res)
        
        # analyze response
        if res == "Login Failed.":
            pass
        elif res == "Disconnected from server.":
            break
        else:
            logged_in_flag = True
        
    if logged_in_flag:
        while True:
            
            cmd = input()
            # check validity of command format (if cmd in format "[cmd_name]: [argument1] [argument2]... [argumentN]" and if it is an existing command, validity of arguments) . If invalid -> send 'quit' command, which disconnects from server, and close program
            try:
                ns.check_cmd_argument_amount(cmd)
                ns.execute(cmd)
            except:
                print("Error - Command arguments are invalid.") # Per instruction, print error msg
                cmd = "quit"
            
            current_msg = ns.OutgoingSocketMessage(cmd)
            cilent_socket.send(current_msg.size.to_bytes(4, 'big')) # send size
            while not current_msg.is_complete(): # sending command
                cilent_socket.send(current_msg.get_data(DATA_BANDWIDTH))
            

            size_in_bytes = cilent_socket.recv(4) 
            size = int.from_bytes(size_in_bytes, "big")
            current_msg = ns.IncomingSocketMessage(size)
            while not current_msg.is_complete():
                current_msg.add_data(cilent_socket.recv(DATA_BANDWIDTH))
            res = current_msg.data.decode(encoding = "utf-8") # command response msg
            print(res)
            if res == "Disconnected from server.":
                break
            
    print("Program finished.")