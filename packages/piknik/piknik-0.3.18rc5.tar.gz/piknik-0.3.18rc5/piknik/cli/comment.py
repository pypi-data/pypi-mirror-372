# standard imports
import sys
import logging

logg = logging.getLogger(__name__)

ctx = None


def subparser(argp):
    argp.add_argument('-s', '--sign-as', dest='s', type=str, help='PGP fingerprint of key to sign issue update with')
    argp.add_argument('-x', '--text', dest='x', type=str, action='append', default=[], help='Add literal message text')
    argp.add_argument('-y', '--file', dest='y', type=str, action='append', default=[], help='Add arbitrary file as content')
    return argp


def assembler(o, arg):
    o.x = arg.x
    o.y = arg.y
    o.s = arg.s


next_i = 1
def next_message_arg():
    global next_i

    r = sys.argv[next_i]

    if r[0] != '-':
        next_i += 1
        return None

    if r[1] not in ['r', 'i', 'x', 'y']:
        next_i += 1
        return None

    v = sys.argv[next_i+1]
    next_i += 2
    return (r[1], v,)


def main():
    messages = []
    while True:
        try:
            r = next_message_arg()
        except IndexError:
            break
        if r == None:
            continue

        if r[0] == 'x':
            messages.append('s:' + r[1])
        elif r[0] == 'y':
            messages.append('f:' + r[1])

    ctx.basket.msg(ctx.issue_id, *messages)

