import numpy as np

focus_table = np.array([0, 5, 10, 30, 10, 20, 25, 20, 23, 50, 10])

focus_local_maxima = (np.diff(np.sign(np.diff(focus_table))) < 0).nonzero()[0] + 1


print(focus_table[focus_local_maxima])
max_focus = np.unique(focus_table[focus_local_maxima])[-1]
second_max_focus = np.unique(focus_table[focus_local_maxima])[-2]

print(focus_local_maxima)

max_focus_index = np.where(focus_table[focus_local_maxima] == max_focus)
second_max_focus_index = np.where(focus_table[focus_local_maxima] == second_max_focus)


