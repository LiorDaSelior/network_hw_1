import numbers_service as ns
import socket as sk
import sys

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 1337
DATA_BANDWIDTH = 4

host = DEFAULT_HOST
port = DEFAULT_PORT
current_msg = None
logged_in_flag = False

if len(sys.argv) == 1:
    host = DEFAULT_HOST
    port = DEFAULT_PORT
elif len(sys.argv) == 2:
    host = sys.argv[1]
    port = DEFAULT_PORT
elif  len(sys.argv) == 3:
    host = sys.argv[1]
    port = int(sys.argv[2])
else:
    raise AttributeError("Client setup failed - Arguments are invalid.")

try:
    with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as cilent_socket:
        
        cilent_socket.connect((host, port))
        
        # recv welcome msg
        size_in_bytes = cilent_socket.recv(4)
        size = int.from_bytes(size_in_bytes, "big")
        current_msg = ns.IncomingSocketMessage(size)
        while not current_msg.is_complete():
            current_msg.add_data(cilent_socket.recv(DATA_BANDWIDTH))
        print(current_msg.data.decode(encoding = "utf-8")) 
        
        while not logged_in_flag:
            
            # login attempt
            first_line_input = input() 
            second_line_input = input()
            current_msg = ns.OutgoingSocketMessage(f"{first_line_input}\n{second_line_input}")
            cilent_socket.send(current_msg.size.to_bytes(4, 'big')) # send login credentials data size
            while not current_msg.is_complete(): # sending login cred credentials data
                cilent_socket.send(current_msg.get_data(DATA_BANDWIDTH))
                
            # recv server response to login
            size_in_bytes = cilent_socket.recv(4) 
            size = int.from_bytes(size_in_bytes, "big")
            current_msg = ns.IncomingSocketMessage(size)
            while not current_msg.is_complete():
                current_msg.add_data(cilent_socket.recv(DATA_BANDWIDTH))
            res = current_msg.data.decode(encoding = "utf-8")
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
                
                # enter command and check validity. If invalid -> send 'quit' command, which disconnects client from server
                cmd = input()
                try:
                    ns.check_cmd_argument_amount(cmd)
                    ns.execute(cmd)
                except:
                    print("Error - Command arguments are invalid.") # per instruction, print error msg
                    cmd = "quit"
                
                current_msg = ns.OutgoingSocketMessage(cmd)
                cilent_socket.send(current_msg.size.to_bytes(4, 'big')) # send command data size
                while not current_msg.is_complete(): # sending command data
                    cilent_socket.send(current_msg.get_data(DATA_BANDWIDTH))
                
                # recv server response to command
                size_in_bytes = cilent_socket.recv(4) 
                size = int.from_bytes(size_in_bytes, "big")
                current_msg = ns.IncomingSocketMessage(size)
                while not current_msg.is_complete():
                    current_msg.add_data(cilent_socket.recv(DATA_BANDWIDTH))
                
                # analyze response
                res = current_msg.data.decode(encoding = "utf-8") 
                print(res)
                if res == "Disconnected from server.":
                    break
                
        print("Program finished.")
except OSError as exception:
    print(exception.strerror)
    print("Socket error encountered. Program finished.")
    exit()