#!/usr/bin/python
import sys
import math
import random

import lib

def control(init, updates):
    """Control the robot."""
    lib.send_command(None, "set-speed 200 set-rotation-speed 30")
    for update in updates:
        if random.random() < 0.01:
            lib.send_command(update, "set-speed %d set-rotation-speed %d" % 
                (random.randrange(-150, 150), random.randrange(-100, 100)))
        my_robot = update["robots"]["me"]
        other_robots = update["robots"]["others"]
        if not other_robots:
            break
        if my_robot["time_to_fire"] or my_robot["turret_rotation"]:
            lib.send_command(update)
            continue
        other_robot = other_robots[0]
        
        # Fire a bullet to the other robot 
        diff_x = other_robot["x"] - my_robot["x"]
        diff_y = other_robot["y"] - my_robot["y"]
        angle = (-math.atan(diff_y / diff_x) if abs(diff_x) > 0.0001 else math.pi / 2.0)
        angle2 = (angle * 180.0 / math.pi) + \
            (180.0 if other_robot["x"] < my_robot["x"] else 0.0)
        #angle3 = angle2 + random.randrange(-10, 10)
        lib.send_command(update, "rotate-turret-to-angle-and-fire %d" % angle2)
        
if __name__ == '__main__':
    sys.exit(lib.main(sys.argv[1:], control))
