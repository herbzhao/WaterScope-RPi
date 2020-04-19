import re

string = "Incubator temp: 127.00*C"
incubator_temp_re = re.compile('Incubator temp:')

string2 = "Defogger temp: 55.94 *C"
defogger_temp_re = re.compile('Defogger temp:')

if incubator_temp_re.findall(string):
    print(float(string.replace('*C','').replace('Incubator temp: ','')))

if defogger_temp_re.findall(string2):
    print(float(string2.replace('*C','').replace('Defogger temp: ','')))