#!/usr/bin/env python3
"""
glide over to check out other frequencies
click to form a chord
blue is the harmony of a given interval
orange is the harmony in a chord
"""
import csv
import glob

import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.stats import rankdata

import survey as sr

# define plot
plt.style.use('dark_background')
fig, ax = plt.subplots()


p, stream = sr.init_audio()

data = []
nick = input('\nchoose nick:\n')
dir_name = sr.get_dir_name(nick)
for file_name in glob.glob(dir_name + '/*'):
    with open(file_name, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            parsed_row = list(map(float, row))
            data.append(parsed_row)

sorted_data = sorted(data)   # sorted by key, return a list of tuples
xs, ys = zip(*sorted_data)      # unpack a list of pairs into two tuples

print('samples loaded: ', len(ys))

ys = rankdata(ys) / len(ys)     # normalize ranking

# TODO use bins instead
smooth = savgol_filter(ys, 15, 3)
# smooth = savgol_filter(smooth, 21, 3)


def draw():
    ax.set_ylim([0, 1])
    notes = [2 ** (i / 12) for i in range(1, 13)]
    for note in notes:
        ax.axvline(x=note, color='purple', linewidth=0.5)
    ax.plot(xs, smooth, 'blue')
    fig.canvas.draw()


def harmony(ratio):
    """
    predict how harmonious given ratio should sound
    ! assumes x's are distributed evenly on 1..2
    """
    if ratio < 1:
        ratio = 1 / ratio
    index = int((ratio-1) * len(data))
    return smooth[index]


def choose_second_frequency(event):
    """
    choose second note of the chord, and play it,
    also display in red predicted harmony of a third note, with the other two
    """
    global CHOSEN_RATIO
    if not event.xdata:
        return

    CHOSEN_RATIO = event.xdata
    player.frequencies = [sr.BASE_FREQUENCY,
                          sr.BASE_FREQUENCY * CHOSEN_RATIO,
                          sr.BASE_FREQUENCY * event.xdata]
    harmony_line = [(harmony(x/1)
                    + harmony(x/CHOSEN_RATIO)
                    + harmony(CHOSEN_RATIO)) / 3
                    for x in xs]
    ax.cla()
    ax.plot(xs, harmony_line, 'red', linewidth=3)
    ax.axvline(x=CHOSEN_RATIO, color='red', linewidth=3)
    draw()


def update_third_frequency(event):
    """
    choose third note of the chord, and play it
    """
    if not event.xdata:
        return

    if event.button == 1:
        choose_second_frequency(event)
        return
    player.frequencies = [sr.BASE_FREQUENCY,
                          sr.BASE_FREQUENCY * CHOSEN_RATIO,
                          sr.BASE_FREQUENCY * event.xdata]


draw()
CHOSEN_RATIO = 0
player = sr.PolyphonicPlayer(stream)
player.start()

fig.canvas.mpl_connect('button_press_event', choose_second_frequency)
fig.canvas.mpl_connect('motion_notify_event', update_third_frequency)

plt.show()
player.kill()  # break the playing loop
player.join()
stream.stop_stream()
stream.close()
p.terminate()







# print accurate data
# plt.plot(x, y, 'ro', markersize=1)

# BINS_NUMBER = 100
# # put data into bins
# bins = [[] for _ in range(BINS_NUMBER)]
# for key in data:
#     bin_index = int((key-1) * BINS_NUMBER)
#     bins[bin_index].append(data[key])
#
# # print bins
# x_range = np.linspace(1, 2, BINS_NUMBER+1)[:-1] + 1/BINS_NUMBER/2
# plt.plot(x_range, [np.mean(bin) for bin in bins])
