#class InvalidCommandArgumentException(Exception):
#    pass

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
    #"User: user1\nPassword: password1"
    #try:
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
    #except:
    #return None






def calculate(x, op, y):
    if op == '-':
        return x - y
    elif  op == '+':
        return x + y
    elif op == '/':
        return x / y
    elif op == '*':
        return x * y
    
def is_palindrome(x):
    i = 0
    m = len(x)
    while i < m / 2:
        if x[i] != x[(m-1)-i]:
            return False
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

command_list = ["calculate", "is_palindrome", "is_prime"]

def execute(cmd_name, cmd_args):
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
    return res

def check_cmd_arguments(cmd_name, cmd_args): #! TODO - Correctness Check
    if cmd_name == "calculate":
        if len(cmd_args) != 3:
            return False
    if cmd_name == "is_palindrome":
        if len(cmd_args) != 1 or not cmd_args[0].isdigit():
            return False
    if cmd_name == "is_prime":
        if len(cmd_args) != 1 or not cmd_args[0].isdigit():
            return False
    return True