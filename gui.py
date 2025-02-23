import pygame
from parameters import *
import time
import numpy as np
import keyboard

margin = 5
zoom = 0.4


def draw(screen, x, y, r, col):
    w = screen.get_width()
    h = screen.get_height()
    pygame.draw.ellipse(screen, col, (x - r + w / 2, y - r + h / 2, 2 * r, 2 * r))


def start(body_list, display=True):
    if display:
        SCREEN = pygame.display.set_mode((screen_width, screen_height))
        SCREEN.fill((0, 0, 0))
    duration = 0
    all_crashes = []
    crashes = []
    escaped = False
    poses = []
    for i in range(len(body_list)):
        poses.append([body_list[i].pos_x, body_list[i].pos_y])
    pos_avg = np.average(poses, axis=0, weights=[body_list[k].radius ** 3 for k in range(len(body_list))])
    center = [10,0]
    while True:
        if display:
            if len(body_list) == 1:
                return len(crashes), escaped, duration
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return len(crashes), escaped, duration
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        SCREEN.fill((0, 0, 0))
                        center[0] -= 10
                    if event.key == pygame.K_RIGHT:
                        SCREEN.fill((0, 0, 0))
                        center[0] += 10
                    if event.key == pygame.K_DOWN:
                        SCREEN.fill((0, 0, 0))
                        center[1] += 10
                    if event.key == pygame.K_UP:
                        SCREEN.fill((0, 0, 0))
                        center[1] -= 10
        if display:
            for i in range(len(body_list)):
                x = (body_list[i].pos_x - pos_avg[0]) * zoom - center[0]
                y = (body_list[i].pos_y - pos_avg[1]) * zoom - center[1]
                r = body_list[i].radius * zoom
                draw(SCREEN, x, y, 2 * r + margin, (0, 0, 0))

        all_crashes.sort()
        for i in all_crashes[::-1]:
            x = (body_list[i].pos_x - pos_avg[0]) * zoom - center[0]
            y = (body_list[i].pos_y - pos_avg[1]) * zoom - center[1]
            r = body_list[i].radius * zoom
            draw(SCREEN, x, y, 2 * r + margin, (0, 0, 0))
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
                pos_avg = np.average(poses, axis=0, weights=[body_list[k].radius ** 3 for k in range(len(body_list))])
                if display:
                    x = (body_list[i].pos_x - pos_avg[0]) * zoom - center[0]
                    y = (body_list[i].pos_y - pos_avg[1]) * zoom - center[1]
                    r = body_list[i].radius * zoom
                    draw(SCREEN, x, y, r, (0, 255, 0))
        if display:
            pygame.display.update()

        if display:
            time.sleep(dt / fastfwd)
        duration += dt
