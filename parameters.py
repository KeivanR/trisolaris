import numpy as np
names = [
    'Trisolaris',
    'Sun 1',
    'Sun 2',
    'Sun 3',
]

radius = [
    10,
    30,
    30,
    30
]
poses = [
    [150, 150],
    [0, 150],
    [150, 0],
    [300, 300],
]
speeds = [
    [0, -20],
    [0, 20],
    [0, -20],
    [20, 0],
]
s_range = [-2,5]
p_range = [0, 300]
r_range = [1,5]
n_bodies = 50
poses = list(np.random.uniform(p_range[0], p_range[1], (n_bodies, 2)))
speeds = list(np.random.uniform(s_range[0], s_range[1], (n_bodies, 2)))
radius = list(np.random.uniform(r_range[0], r_range[1], n_bodies))
names = ['']*n_bodies

#CONSTANTS
G = 8
dt = 0.01
fastfwd = 10
screen_width = 1200
screen_height = 1000
