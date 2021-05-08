
import pprint

def exit_with_error(message: str):
    FAILURE = 1
    print(message)
    exit(FAILURE)
    
def is_tuple(obj):
    return True if type(obj) is tuple else False

def print_pretty(matrix):
    pp = pprint.PrettyPrinter(depth=3)

    s = [[str(e) for e in row] for row in matrix]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    print("\n".join(table))