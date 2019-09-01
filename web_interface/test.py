import serial
import time

focus_table = {1000: 50, 2000: 100, 3000: 20}
print(max(focus_table, key=focus_table.get))

a = 123.4566677

print('value: {0:.0f}'.format(a))