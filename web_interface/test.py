import yaml        
        
with open('config_serial.yaml') as config_serial_file:
    serial_controllers_config = yaml.load(config_serial_file)
serial_controllers_names = []

for board_name in serial_controllers_config:
    if serial_controllers_config[board_name]['connect'] is True:
        serial_controllers_names.append(board_name)

print(serial_controllers_names)