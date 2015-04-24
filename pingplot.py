from queue import Queue, Empty
from threading import Thread
from subprocess import Popen, PIPE
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import time
import sys


def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        try:
            l = float(line.decode('utf-8').split(' ')[7].split('=')[1])
            data = (datetime.now(), l)
            queue.put(data)
            print(data)
        except:
            pass
    out.close()




if __name__ == "__main__":
    host = sys.argv[1]

    p = Popen(['ping', host], stdout=PIPE,
              bufsize=1, close_fds=True)
    q = Queue()
    t = Thread(target=enqueue_output, args=(p.stdout, q))
    t.daemon = True  # thread dies with the program
    t.start()

    data = []

    def get_data():
        while True:
            try:
                data.append(q.get_nowait())
            except Empty:
                return data

    plt.ion()
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)

    while True:
        time.sleep(10)
        x, y = zip(*get_data())
        print(len(x))
        ax1.clear()
        ax1.plot(x, y, 'ro')
        fig.autofmt_xdate()
        ax1.fmt_xdata = mdates.DateFormatter('%H-%m-%s')
        fig.canvas.draw()
        fig.canvas.flush_events()
        print("here")

    # # read line without blocking
    # while True:
    #     try:
    #         line = q.get_nowait() # or q.get(timeout=.1)
    #     except Empty:
    #         pass
    #         #print('no output yet')
    #     else: # got line
    #         # ... do something with line
    #         print(line)
