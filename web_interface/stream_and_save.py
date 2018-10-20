# TEST: this is used to test the stealing form stream

import io
import time
import threading

class stream_stealer_class():
    def __init__(self):
        self.stream = io.BytesIO()
        
    def write_stream(self):
        while True:
            self.stream.write(b'hello \n')
            time.sleep(1)
    
    def write_stream_thread(self):
        self.threading_writing = threading.Thread(target=self.write_stream)
        self.threading_writing.daemon = True
        self.threading_writing.start()
    
    def read_stream(self):
        while True:
            self.stream.seek(0)
            self.stream.truncate()
            time.sleep(0.1)
            # yield the result to be read
            frame = self.stream.getvalue()
            ''' ensure the size of package is right''' 
            if len(frame) == 0:
                pass
            else:
                print(frame)
                # this is used only for saving to file purpose
                self.valid_frame = frame
    
    def read_stream_thread(self):
        self.threading_reading = threading.Thread(target=self.read_stream)
        self.threading_reading.daemon = True
        self.threading_reading.start()

    def stream_saving(self, time_int=10):
        time_start = time.time()
        self.close_flag = False
        with open('test.txt', 'a+') as f:
            while True:
                time_now = time.time()
                try:
                    f.write(str(self.valid_frame))
                    # after capturing it, destorying the frame
                    del(self.valid_frame)
                    print('write now')
                except AttributeError:
                    time.sleep(0.1)

                # when time is too long, automatically close
                if time_now - time_start >=10:
                    self.close_flag = True
            
                if self.close_flag is True:
                    break
    
    def stream_saving_thread(self):
        self.threading_stream_saving = threading.Thread(target=self.stream_saving)
        self.threading_stream_saving.daemon = True
        self.threading_stream_saving.start()



if __name__ == "__main__":
    stream_stealer = stream_stealer_class()
    stream_stealer.write_stream_thread()
    stream_stealer.read_stream_thread()
    stream_stealer.stream_saving_thread()
    time.sleep(5)
    stream_stealer.close_flag = True

    while True:
        pass
