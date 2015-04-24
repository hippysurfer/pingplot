from Queue import Queue, Empty
from threading import Thread
from subprocess import Popen, PIPE
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import time
import sys


def enqueue_output(out, err, queue):
    try:
        for line in iter(out.readline, b''):
            try:
                l = float(line.decode('utf-8').split(' ')[6].split('=')[1])
                data = (datetime.now(), l)
                queue.put(data)
            except Exception, e:
                print(line)
                print(e)
                pass
    except:
        print("Error reading from ping",err.readlines())
    finally:
        out.close()
        err.close()




if __name__ == "__main__":
    host = sys.argv[1]

    p = Popen(['ping', '-i', '0.001', host], stdout=PIPE,
              stderr=PIPE, bufsize=1, close_fds=True)
    q = Queue()
    t = Thread(target=enqueue_output, args=(p.stdout, p.stderr, q))
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

