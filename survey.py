#!/usr/bin/env python3
"""
plays randomly chosen two notes
asks user to rate how harmonious they sound
saves gathered data
"""

import curses
import pickle
import threading
from time import time, sleep

import numpy as np
import pyaudio


BIT_RATE = 44000
BASE_FREQUENCY = 200
help_msg = """
rate how harmonious this sounds on a scale from 1 to 9
press q to quit

"""

# credit: stackoverflow.com/questions/10702942/note-synthesis-harmonics-violin-piano-guitar-bass-frequencies-midi
violin_amps = [0.0, 1.0, 0.286699025, 0.150079537, 0.042909002,
               0.203797365, 0.229228698, 0.156931925,
               0.115470898, 0.0, 0.097401803, 0.087653465,
               0.052331036, 0.052922462, 0.038850593,]
               # 0.053554676, 0.053697434, 0.022270261,
               # 0.013072562, 0.008585879, 0.005771505,
               # 0.004343925, 0.002141371, 0.005343231,
               # 0.000530244, 0.004711017, 0.009014153]

piano_amps = [0.0, 1.0, 0.399064778, 0.229404484, 0.151836061,
              0.196754229, 0.093742264, 0.060871957,
              0.138605419, 0.010535002, 0.071021868,]
              # 0.029954614, 0.051299684, 0.055948288,
              # 0.066208224, 0.010067391, 0.00753679,
              # 0.008196947, 0.012955577, 0.007316738,]
              # 0.006216476, 0.005116215, 0.006243983,
              # 0.002860679, 0.002558108, 0.0, 0.001650392]


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
    segment_duration = 0.01     # in seconds
    amps = piano_amps          # tone (amplitude of the overtones)

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

    def get_wave(self, primary_frequency, phase):
        acc = 0
        for index, amplitude in enumerate(self.amps):
            frequency = primary_frequency * index
            wave = np.sin(2 * np.pi *
                          np.arange(BIT_RATE * self.segment_duration) *
                          frequency / BIT_RATE
                          + phase * index)
            acc += wave * amplitude
        # adjust volume
        maximum_possible_volume = np.sum(self.amps)
        return acc / maximum_possible_volume

    def kill(self):
        self.alive = False


def init():
    # load data
    print('choose nick:')
    filename = "data/%s.pickle" % 'filip'
    try:
        data = pickle.load(open(filename, "rb"))
    except IOError:
        # the file doesn't exist
        data = {}
    print('data length: %d' % len(data))

    # initialize pyaudio
    p = pyaudio.PyAudio()
    # for paFloat32 sample values must be in range [-1.0, 1.0]
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=BIT_RATE,
                    output=True)
    return data, p, stream, filename


if __name__ == '__main__':
    data, p, stream, filename = init()

    # survey until interrupted
    try:
        while True:
            ratio = 1 + np.random.random()  # between 1 and 2

            player = PolyphonicPlayer(stream)
            first_frequency = np.random.randint(BASE_FREQUENCY, BASE_FREQUENCY * 2)
            second_frequency = first_frequency * ratio
            player.frequencies = [first_frequency, second_frequency]

            player.start()          # start playing in a loop
            rating = int(input_char())   # get user rating from 1 to 9

            player.kill()           # break the playing loop
            player.join()
            data[ratio] = rating    # save the rating

    except:
        # program interrupted
        pickle.dump(data, open(filename, "wb"))

        stream.stop_stream()
        stream.close()
        p.terminate()
