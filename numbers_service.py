# classes and methods of message handling:
class SocketMessage():
    def __init__(self, size: int, data: bytes) -> None:
        self.data = data
        self.size = size
        
class IncomingSocketMessage(SocketMessage):
    def __init__(self, size: int) -> None:
        super().__init__(size, b"")
    
    def add_data(self, data: bytes) -> None:
        self.data += data
        
    def is_complete(self):
        return self.size == len(self.data)
        
class OutgoingSocketMessage(SocketMessage):
    def __init__(self, msg: str) -> None:
        data = msg.encode()
        super().__init__(len(data), data)
    
    def get_data(self, size: int) -> bytes:
        res_data = self.data[:size]
        self.data = self.data[size:]
        return res_data
    
    def is_complete(self):
        return len(self.data) == 0


# methods for user info and login management:
def get_user_info(user_data_filename):
    res = {}
    with open(user_data_filename, 'r', encoding="utf-8") as user_data_file:
        for row in user_data_file.read().splitlines():
            row_iter = row.split('\t')
            res[row_iter[0]] = row_iter[1]
    return res

def login(user_cred_str, user_data):
    user_cred = get_cred(user_cred_str)
    if user_cred is None:
        return None
    else:
        user_name = user_cred[0]
        user_password = user_cred[1]
        if user_name in user_data and user_data[user_name] == user_password:
            return True
    return False

def get_cred(user_cred_str): # return None if format is invalid, otherwise return (user, password) tuple (this also accounts for quit)
    user_cred_arr = user_cred_str.split('\n')
    if len(user_cred_arr) != 2:
        return None
    
    user_name_str = user_cred_arr[0]
    user_password_str = user_cred_arr[1]
    
    user_name_arr = user_name_str.split(' ')
    if len(user_name_arr) != 2:
        return None
    user_name_prefix = user_name_arr[0]
    user_name = user_name_arr[1]
    if user_name_prefix != "User:":
        return None

    user_password_arr = user_password_str.split(' ')
    if len(user_password_arr) != 2:
        return None
    user_password_prefix = user_password_arr[0]
    user_password = user_password_arr[1]
    if user_password_prefix != "Password:":
        return None
    
    return (user_name, user_password)

# methods for handling user commands:
def calculate(x, op, y):
    if op == '-':
        return x - y
    elif  op == '+':
        return x + y
    elif op == '/':
        return round((x / y) * 100) / 100.0
    elif op == '*':
        return x * y
    else:
        raise AttributeError()
    
def is_palindrome(x):
    x = str(x)
    i = 0
    m = len(x)
    while i < m / 2:
        if x[i] != x[(m-1)-i]:
            return False
        i += 1
    return True

def is_prime(x):
    if x == 0 or x == 1:
        return False
    if x == 2:
        return True
    if x % 2 == 0:
        return False
    for i in range(3, int(x ** 0.5 + 1), 2):
        if x % i == 0:
            return False
    return True

def execute(cmd): # Assumption: Command and it's arguments are valid, because user program checks for errors and invalid commands, therefore no error handling
    cmd_arr = cmd.split(": ")
    if len(cmd_arr) == 1: # command is in the right format ([cmd_name]) but is unknown to server - also account for quit command
        return None
    cmd_name = cmd_arr[0]
    cmd_args = ((cmd_arr[1])).split(" ")
    res = ""
    if cmd_name == "calculate":
        res = calculate(int(cmd_args[0]), cmd_args[1], int(cmd_args[2]))
        res = str(res)
    elif cmd_name == "is_palindrome":
        res = is_palindrome(int(cmd_args[0]))
        res = "Yes" if res else "No"
    elif cmd_name == "is_prime":
        res = is_prime(int(cmd_args[0]))
        res = "Yes" if res else "No"
    else: # command is in the right format ([cmd_name]: [argument1] [argument2]... [argumentN]) but is unknown to server
        return None
    return res

def check_cmd_argument_amount(cmd): # check arguments format correctness
    if cmd == "quit":
        return
    cmd_arr = cmd.split(": ")
    cmd_name = cmd_arr[0]
    cmd_args = ((cmd_arr[1])).split(" ")
    check_dict = {"calculate": 3, "is_palindrome": 1, "is_prime": 1}
    for key in check_dict.keys():
        if cmd_name == key:
            if len(cmd_args) != check_dict[key]:
                raise AttributeError()