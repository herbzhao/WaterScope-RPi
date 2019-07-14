# regex for parsing the output
import re

serial_output = 'Average sensor: 37.5 *C'

temp_re = re.compile('Average sensor:\s\d+.\d+\s\*C')

if temp_re.findall(serial_output):
    print(float(serial_output.replace(' *C','').replace('Average sensor: ','')))