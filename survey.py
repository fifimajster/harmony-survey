import curses
import pickle
import threading
from time import time, sleep

import numpy as np
import pyaudio  # sudo apt-get install python-pyaudio

BIT_RATE = 44000
help_msg = """
rate how harmonious this sounds on a scale from 1 to 9
press q to quit

"""

p = pyaudio.PyAudio()     # initialize pyaudio

# for paFloat32 sample values must be in range [-1.0, 1.0]
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=BIT_RATE,
                output=True)


def input_char():
    """
    get single char from stdin without pressing enter
    credit: stackoverflow.com/questions/3523174/raw-input-in-python-without-pressing-enter
    """
    try:
        win = curses.initscr()
        win.addstr(0, 0, help_msg)
        while True:
            ch = win.getch()
            if ch == 'q':
                raise KeyboardInterrupt
            if ch in range(32, 127):
                break
            sleep(0.01)
    except:
        raise
    finally:
        curses.endwin()
    return chr(ch)


class PolyphonicPlayer(threading.Thread):
    segment_duration = 0.01  # seconds

    def __init__(self, stream):
        threading.Thread.__init__(self)
        self.stream = stream
        self.alive = True
        self.frequencies = []
        self.phases = [0, 0, 0, 0, 0, 0, 0]
        self.last_time = time()

    def run(self):
        while self.alive:
            if not self.frequencies:
                # no frequencies given so be silent
                sleep(self.segment_duration)
                continue

            # construct a sound
            new_time = time()
            final_sound = 0
            for i, frequency in enumerate(self.frequencies):
                final_sound += self.get_wave(frequency, self.phases[i])
                self.phases[i] += self.segment_duration * frequency * 2*np.pi
                self.phases[i] %= 2*np.pi

            final_sound /= len(self.frequencies)    # adjust volume

            self.last_time = new_time
            self.stream.write(final_sound
                              .astype(np.float32)
                              .tobytes())

    def get_wave(self, frequency, phase):
        return np.sin(2 * np.pi *
                      np.arange(BIT_RATE * self.segment_duration) *
                      frequency / BIT_RATE
                      + phase)

    def kill(self):
        self.alive = False


if __name__ == '__main__':
    print('\nchoose nick:')
    filename = "data/%s.pickle" % input()
    try:
        data = pickle.load(open(filename, "rb"))
    except IOError:
        # the file doesn't exist
        data = {}

    try:
        while True:
            BASE_FREQUENCY = np.random.randint(300, 500)
            ratio = 1 + np.random.random()  # between 1 and 2

            player = PolyphonicPlayer(stream)
            player.frequencies = [BASE_FREQUENCY, BASE_FREQUENCY * ratio]

            player.start()          # start playing in a loop
            rating = int(input_char())   # get user rating from 1 to 9

            player.kill()           # break the playing loop
            player.join()
            data[ratio] = rating    # save the rating

    except:
        # program interrupted
        # print(e)

        pickle.dump(data, open(filename, "wb"))

        stream.stop_stream()
        stream.close()
        p.terminate()
