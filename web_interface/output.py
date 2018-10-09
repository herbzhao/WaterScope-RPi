import time
import threading
import numpy as np

class output_class_builder(object):
    def __init__(self):
        pass

    def produce_output(self):
        self.x = 0
        while True:
            self.x += 0.2
            self.y = np.random.rand()*100
            time.sleep(0.2)


    def output_threading(self):
        # now threading1 runs regardless of user input
        self.output_thread = threading.Thread(target=self.produce_output)
        self.output_thread.daemon = True
        self.output_thread.start()


if __name__ == '__main__':
    output_class = output_class_builder()
    output_class.output_threading()
    while True:
        pass