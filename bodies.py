import numpy as np
import math
from parameters import *


class body:
    def __init__(self, radius, pos_x, pos_y, speed_x, speed_y, name='Unnamed'):
        self.radius = radius
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.name = name

    def move(self, body_list):
        escaped = False
        crashes = []
        for i in range(len(body_list)):
            if body_list[i].pos_x != self.pos_x or body_list[i].pos_y != self.pos_y:
                theta = math.atan2(body_list[i].pos_y - self.pos_y, body_list[i].pos_x - self.pos_x)
                r2 = (self.pos_x - body_list[i].pos_x) ** 2 + (self.pos_y - body_list[i].pos_y) ** 2
                if r2 > 400 ** 2:
                    escaped = True
                if r2 < (self.radius + body_list[i].radius) ** 2:
                    self.pos_x = (self.radius**3*self.pos_x+body_list[i].radius**3*body_list[i].pos_x)/(self.radius**3+body_list[i].radius**3)
                    self.pos_y = (self.radius**3*self.pos_y+body_list[i].radius**3*body_list[i].pos_y)/(self.radius**3+body_list[i].radius**3)
                    self.speed_x = (self.radius**3*self.speed_x+body_list[i].radius**3*body_list[i].speed_x)/(self.radius**3+body_list[i].radius**3)
                    self.speed_y = (self.radius**3*self.speed_y+body_list[i].radius**3*body_list[i].speed_y)/(self.radius**3+body_list[i].radius**3)
                    self.radius = (self.radius**3 + body_list[i].radius**3)**(1/3)
                    crashes.append(i)
                else:
                    acc_x = G * body_list[i].radius**3 / r2 * math.cos(theta)
                    acc_y = G * body_list[i].radius**3 / r2 * math.sin(theta)
                    self.speed_x += acc_x * dt
                    self.speed_y += acc_y * dt
                    self.pos_x += self.speed_x * dt
                    self.pos_y += self.speed_y * dt
        return escaped, crashes
