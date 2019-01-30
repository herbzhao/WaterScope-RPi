import numpy as np

# create the optimal focus curve
ascend = np.linspace(1, 10, 100) 
descend = np.linspace(10, 1, 100)

noisy_ascend = [i+(np.random.random()-0.5) for i in ascend]
noisy_descend = [i+(np.random.random()-0.5) for i in descend]

total_path = noisy_ascend+noisy_descend
print(total_path)

step_size = 5
total_length = len(total_path)
total_steps = int(total_length/step_size)

step_map = [step_number*step_size for step_number  in range(total_steps)]
value_map = [total_path[step_coordinate] for step_coordinate in step_map]

print(value_map)
print(step_map)
local_maxima_step = value_map.index(np.max(value_map))
print(step_map[local_maxima_step])
print(value_map[local_maxima_step])


# produce a new step map near the local maxima
step_size = 2
total_length = len(total_path)
total_steps = int(total_length/step_size)

step_map = [step_number*step_size for step_number  in range(total_steps)]
value_map = [total_path[step_coordinate] for step_coordinate in step_map]

print(value_map)
print(step_map)
local_maxima_step = value_map.index(np.max(value_map))
print(step_map[local_maxima_step])
print(value_map[local_maxima_step])

