#class InvalidCommandArgumentException(Exception):
#    pass
    

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