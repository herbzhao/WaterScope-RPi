import time
import threading

def print_with_sleep():
    for i in range(10):
        time.sleep(1)
        print(i)

print_thread = threading.Thread(target=print_with_sleep)
print_thread.daemon = False
print_thread.start()


for i in range(10):
    time.sleep(0.5)
    print(i)