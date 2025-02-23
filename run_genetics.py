import numpy as np
import sys

import bodies
import gui
sys.path.insert(1, '/home/keivan/Documents/Python/genetics')

import genetics

s_range = [-3, 3]
p_range = [0, 300]
r_trisolaris = 3
r_suns = 30
n_bodies = 4
n_individuals = 1000
mutation_strength = 0.1

radius = [r_trisolaris] + [r_suns] * n_bodies
names = ['Trisolaris', 'Sun1', 'Sun2', 'Sun3']

poses = np.random.uniform(p_range[0], p_range[1], (n_individuals, n_bodies, 2))
speeds = np.random.uniform(s_range[0], s_range[1], (n_individuals, n_bodies, 2))

individuals = list(np.concatenate((poses, speeds), 2))
mutation_sigma = np.array([p_range[1]-p_range[0]]*2+[s_range[1]-s_range[0]]*2)*mutation_strength

def run_body_movement(ind, show):
    body_list = []
    for i in range(n_bodies):
        body_list.append(
            bodies.body(
                radius[i],
                ind[i, 0],
                ind[i, 1],
                ind[i, 2],
                ind[i, 3],
                name=names[i]
            )
        )
    _, _, duration = gui.start(body_list, display=show)
    return duration


def simul(ind):
    return run_body_movement(ind, show=False)


def simul_display(ind):
    return run_body_movement(ind, show=True)


def mutate(ind, n_children, sigma):
    return list(np.random.normal(
        ind,
        sigma,
        (n_children, ind.shape[0], ind.shape[1])
    ))


selectivity = 2
n_generations = 10000
display_freq = 10000

genetics.run(
    individuals,
    simul,
    simul_display,
    mutate,
    mutation_sigma,
    selectivity,
    n_generations,
    display_freq,
    verbose=True
)
