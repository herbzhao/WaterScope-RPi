from threading import Timer
import time

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

def hello():
    print("hello, world")

timer = RepeatTimer(1, hello)
timer.start()
time.sleep(5)
timer.cancel()