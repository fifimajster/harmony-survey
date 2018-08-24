import pickle
import threading
from time import time, sleep

import numpy as np
import pyaudio  # sudo apt-get install python-pyaudio

BITRATE = 44000
BASE_FREQUENCY = 300
DURATION = 0.01  # seconds

p = pyaudio.PyAudio()     # initialize pyaudio

# for paFloat32 sample values must be in range [-1.0, 1.0]
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=BITRATE,
                output=True)


class PolyphonicPlayer(threading.Thread):
    def __init__(self, stream, segment_duration):
        threading.Thread.__init__(self)
        self.stream = stream
        self.segment_duration = segment_duration
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
                self.phases[i] += (self.segment_duration) * frequency * 2*np.pi
                self.phases[i] %= 2*np.pi

            final_sound /= len(self.frequencies)    # adjust volume

            self.last_time = new_time
            self.stream.write(final_sound
                              .astype(np.float32)
                              .tobytes())

    def get_wave(self, frequency, phase):
        return np.sin(2*np.pi *
                      np.arange(BITRATE * self.segment_duration) *
                      frequency / BITRATE
                      + phase)

    def kill(self):
        self.alive = False


if __name__ == '__main__':
    filename = input('choose nick:') + ".pickle"
    try:
        data = pickle.load(open(filename, "rb"))
    except:
        # the file doesn't exist
        data = {}

    phi = (1 + np.sqrt(5)) / 2
    ratio = 1 + np.random.random()  # initialize as random value between 1 and 2
    print("rate how harmonious this sounds on a scale from 1 to 9")

    try:
        while True:
            # BASE_FREQUENCY = np.random.randint(200, 500)
            player = PolyphonicPlayer(stream, DURATION)
            player.frequencies = [BASE_FREQUENCY, BASE_FREQUENCY * ratio]

            player.start()          # start playing in a loop
            rating = int(input())   # get user rating from 1 to 9
            player.kill()           # break the playing loop
            player.join()

            data[ratio] = rating    # save the rating

            # update ratio
            ratio = (ratio + 1/phi) % 1     # move around inside 0..1 range by golden ratio
            ratio += 1          # must be between 1 and 2

    except Exception as e:
        # program interrupted
        # print(e)

        pickle.dump(data, open(filename, "wb"))

        stream.stop_stream()
        stream.close()

        p.terminate()
