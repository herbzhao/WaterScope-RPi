import yaml
serial_controllers_settings = {
    'waterscope' : {'port_names' : ['ws'], 'baudrate': 9600, 'serial_read_options': ['quiet']},
    'ferg': {'port_names' : ['Micro'], 'baudrate': 115200, 'serial_read_options': ['quiet']},
    # Change: the folder name for serial_read_options[1]
    'para': {'port_names' : ['SERIAL'], 'baudrate': 9600, 'serial_read_options': ['logging', 'heatmass_PID']},
}


with open('arduino_config.yaml', 'w+') as config_file:
    config_file.write(yaml.dump(serial_controllers_settings))
