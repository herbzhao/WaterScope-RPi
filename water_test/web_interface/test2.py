import sys

if len(sys.argv) > 3:
    print('Fourth {}'.format(sys.argv[3]))
elif len(sys.argv) > 2:
    print('Third {}'.format(sys.argv[2]))
elif len(sys.argv) > 1:
    print('Second {}'.format(sys.argv[1]))
else:
    print('first {}'.format(sys.argv[0]))
    

