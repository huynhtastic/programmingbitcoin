import sys

def print_cmds(cmds):
    for cmd in cmds:
        try:
            print(cmd)
            exec(cmd)
        except Exception as err:
            print('{}: {}'.format(type(err), str(err)))
    print()


cmd1 = 'from Point import Point'
cmd2 = 'p1 = Point(-1, -1, 5, 7)'
cmd3 = 'p2 = Point(-1, -2, 5, 7)'
cmds = [cmd1, cmd2, cmd3]

print_cmds(cmds)
