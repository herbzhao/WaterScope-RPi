def serial_write(serial_command, parser = ''):
    ''' sending the parsed serial_commands'''
    if parser == 'waterscope':
        print('waterscope')
    elif parser == 'fergboard' or parser == 'ferg':
        print('ferg')
    else:
        serial_command = serial_command
    print(serial_command)

serial_write('abc', parser = 'ferg123')