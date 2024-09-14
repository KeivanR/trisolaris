import pygame
from parameters import *
import time
import numpy as np

margin = 5


def start(body_list, display=True):
    if display:
        SCREEN = pygame.display.set_mode((screen_width, screen_height))
        SCREEN.fill((0, 0, 0))
    duration = 0
    pos_tot = np.average(poses, axis=0, weights=[body_list[k].radius**3 for k in range(len(body_list))])
    translate = [screen_width // 2 - pos_tot[0], screen_height // 2 - pos_tot[1]]
    all_crashes = []
    while True:
        if display:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
        if display:
            for i in range(len(body_list)):
                x = body_list[i].pos_x + translate[0]
                y = body_list[i].pos_y + translate[1]
                r = body_list[i].radius
                pygame.draw.ellipse(SCREEN, (0, 0, 0),
                                    (x - r - margin, y - r - margin, 2 * r + 2 * margin, 2 * r + 2 * margin))

        pos_tot = np.average(poses, axis=0, weights=[body_list[k].radius**3 for k in range(len(body_list))])
        translate = [screen_width // 2 - pos_tot[0], screen_height // 2 - pos_tot[1]]

        all_crashes.sort()
        for i in all_crashes[::-1]:
            body_list.pop(i)
            poses.pop(i)
        all_crashes = []
        for i in range(len(body_list)):
            if i not in all_crashes:
                escaped, crashes = body_list[i].move(body_list)
                all_crashes = list(set(all_crashes) or set(crashes))
                if not display and (len(crashes) or escaped):
                    return len(crashes), escaped, duration
                poses[i] = [body_list[i].pos_x, body_list[i].pos_y]

                x = body_list[i].pos_x + translate[0]
                y = body_list[i].pos_y + translate[1]
                r = body_list[i].radius
                if display:
                    pygame.draw.ellipse(SCREEN, (0, 255, 0), (x - r, y - r, 2 * r, 2 * r))
        if display:
            pygame.display.update()

        if display:
            time.sleep(dt/fastfwd)
        duration += dt
