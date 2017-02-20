command_string = 'G01 {}{} F{}'.format('abc','def','xyz')
command_byte = command_string.encode(encoding='UTF-8')
print(command_byte)