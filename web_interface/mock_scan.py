import numpy as np

# create the optimal focus curve
ascend = np.linspace(1, 10, 1000) 
descend = np.linspace(10, 1, 1000)

noisy_ascend = [i+(np.random.random()-0.5) for i in ascend]
noisy_descend = [i+(np.random.random()-0.5) for i in descend]

print(noisy_ascend)
