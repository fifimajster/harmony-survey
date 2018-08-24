import pickle
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import survey as sr

'''
glide over to olcheck out other frequencies
click to form a chord
blue is the harmony of a given interval
orange is the harmony in a chord
'''

plt.style.use('dark_background')
fig, ax = plt.subplots()
ax.set_ylim([2, 9])


def redraw():
    ax.set_ylim([2, 9])
    notes = [2**(i/12) for i in range(1, 13)]
    for note in notes:
        ax.axvline(x=note, color='purple', linewidth=0.5)
    fig.canvas.draw()


# load data
filename = input() + ".pickle"
data = pickle.load(open(filename, "rb"))
print(len(data))

lists = sorted(data.items())   # sorted by key, return a list of tuples
xs, ys = zip(*lists)  # unpack a list of pairs into two tuples


# print smoothed data
smooth = savgol_filter(ys, 15, 3)
# smooth = savgol_filter(smooth, 21, 3)
ax.plot(xs, smooth, 'blue')


def harmony(ratio):
    # assuming x's are distributed evenly on 1..2
    if ratio < 1:
        ratio = 1 / ratio
    index = int((ratio-1) * len(data))
    return smooth[index]


# update
CHOSEN_RATIO = 0
player = sr.PolyphonicPlayer(sr.stream, sr.DURATION)
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
