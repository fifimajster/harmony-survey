"""
glide over to check out other frequencies
click to form a chord
blue is the harmony of a given interval
orange is the harmony in a chord
"""

import pickle

import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.stats import rankdata

import survey as sr


# credit: stackoverflow.com/questions/10702942/note-synthesis-harmonics-violin-piano-guitar-bass-frequencies-midi
violin_amps = [1.0, 0.286699025, 0.150079537, 0.042909002,
            0.203797365, 0.229228698, 0.156931925,
            0.115470898, 0.0, 0.097401803, 0.087653465,
            0.052331036, 0.052922462, 0.038850593,
            0.053554676, 0.053697434, 0.022270261,
            0.013072562, 0.008585879, 0.005771505,
            0.004343925, 0.002141371, 0.005343231,
            0.000530244, 0.004711017, 0.009014153]

piano_amps = [1.0, 0.399064778, 0.229404484, 0.151836061,
            0.196754229, 0.093742264, 0.060871957,
            0.138605419, 0.010535002, 0.071021868,
            0.029954614, 0.051299684, 0.055948288,
            0.066208224, 0.010067391, 0.00753679,
            0.008196947, 0.012955577, 0.007316738,
            0.006216476, 0.005116215, 0.006243983,
            0.002860679, 0.002558108, 0.0, 0.001650392]


plt.style.use('dark_background')
fig, ax = plt.subplots()


def redraw():
    ax.set_ylim([0, 1])
    notes = [2**(i/12) for i in range(1, 13)]
    for note in notes:
        ax.axvline(x=note, color='purple', linewidth=0.5)
    fig.canvas.draw()


def main():
    # load data
    print('\nchoose nick:')
    filename = "data/%s.pickle" % input()
    data = pickle.load(open(filename, "rb"))
    print('data length: %d' % len(data))

    sorted_data = sorted(data.items())   # sorted by key, return a list of tuples
    xs, ys = zip(*sorted_data)      # unpack a list of pairs into two tuples
    ys = rankdata(ys) / len(ys)     # normalize ranking

    # print smoothed data
    smooth = savgol_filter(ys, 15, 3)
    # smooth = savgol_filter(smooth, 21, 3)
    redraw()
    ax.plot(xs, smooth, 'blue')

    def harmony(ratio):
        # assuming x's are distributed evenly on 1..2
        if ratio < 1:
            ratio = 1 / ratio
        index = int((ratio-1) * len(data))
        return smooth[index]

    # update
    CHOSEN_RATIO = 0
    player = sr.PolyphonicPlayer(sr.stream)
    player.start()

    def update_third_frequency(event):
        if event.button == 1:
            choose_second_frequency(event)
            return
        player.frequencies = [sr.BASE_FREQUENCY,
                              CHOSEN_RATIO,
                              sr.BASE_FREQUENCY * event.xdata]

    def choose_second_frequency(event):
        global CHOSEN_RATIO
        CHOSEN_RATIO = event.xdata
        player.frequencies = [sr.BASE_FREQUENCY,
                              sr.BASE_FREQUENCY * CHOSEN_RATIO,
                              sr.BASE_FREQUENCY * event.xdata]
        harmony_line = [(harmony(x/1)
                        + harmony(x/CHOSEN_RATIO)
                        + harmony(CHOSEN_RATIO)) / 3
                        for x in xs]
        base_line = [(harmony(x/1)
                      + harmony(x/1)
                      + harmony(1)) / 3
                     for x in xs]
        ax.cla()
        ax.plot(xs, base_line, 'blue', linewidth=1)
        ax.plot(xs, harmony_line, 'red', linewidth=3)
        redraw()

    fig.canvas.mpl_connect('motion_notify_event', update_third_frequency)
    fig.canvas.mpl_connect('button_press_event', choose_second_frequency)

    plt.show()
    sr.stream.stop_stream()
    sr.stream.close()
    sr.p.terminate()


if __name__ == '__main__':
    main()












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
