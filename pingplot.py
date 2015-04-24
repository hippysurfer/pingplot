try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty

from threading import Thread
from subprocess import Popen, PIPE
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime
import sys


def enqueue_output(out, err, queue):
    try:
        for line in iter(out.readline, b''):
            try:
                l = float(line.decode('utf-8').split(' ')[6].split('=')[1])
                data = (datetime.now(), l)
                queue.put(data)
                print(repr(data))
            except Exception, e:
                print(line)
                print(e)
    except:
        print("Error reading from ping", err.readlines())
    finally:
        out.close()
        err.close()

if __name__ == "__main__":
    ping_args = sys.argv[1:]

    p = Popen(['ping']+ping_args, stdout=PIPE,
              stderr=PIPE, bufsize=1, close_fds=True)
    q = Queue()
    t = Thread(target=enqueue_output, args=(p.stdout, p.stderr, q))
    t.daemon = True  # thread dies with the program
    t.start()

    xdata = np.array([])
    ydata = np.array([])

    def get_data():
        global xdata
        global ydata
        while True:
            try:
                x, y = q.get_nowait()
                xdata = np.append(xdata, [x,])
                ydata = np.append(ydata, [y,])
            except Empty:
                return (xdata, ydata)

    plt.ion()
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    xa, = ax1.plot([], [], 'ro')
    plt.title('Ping times')
    plt.xlabel('Time')
    plt.ylabel('ICMP Response (ms)')
    plt.show()

    l = None
    while True:
        x, y = get_data()
        print(len(x))
        #ax1.clear()
        ax1.plot(x, y, 'r+')
        if l:
            l.remove()
        mean = y.mean()
        l = ax1.axhline(mean, color='b', linestyle='dashed', linewidth=2)
        fig.autofmt_xdate()
        ax1.fmt_xdata = mdates.DateFormatter('%H-%m-%S')
        plt.pause(1)
