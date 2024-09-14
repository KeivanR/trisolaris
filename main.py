import bodies
import gui
from parameters import *


n_tries = 1
results = ["Crashed", "Escaped"]
max_duration = 0
n_bodies = 30
for k in range(n_tries):
    body_list = []
    for i in range(len(names)):
        body_list.append(
            bodies.body(
                radius[i],
                poses[i][0],
                poses[i][1],
                speeds[i][0],
                speeds[i][1],
                name=names[i]
            )
        )
    n_crashes, escaped, duration = gui.start(body_list, display=True)
    if duration>max_duration:
        max_duration=duration
        best_poses = poses
        best_speeds = speeds
    # print("*"*200)
    # print('POSES:',poses)
    # print("SPEEDS", speeds)
    # print("RESULTS:", results[err-1], duration)
    # print("*"*200)
#print(max_duration, best_poses, best_speeds)
