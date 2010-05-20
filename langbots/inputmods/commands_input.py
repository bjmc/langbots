#!/usr/bin/python
import sys
import subprocess

# Third-party modules
import yaml

# App modules
from langbots import lib
from langbots import battlefield

def get_state(field, my_robot):
    """Return a string containing Yaml representation of field."""
    is_my_robot = lambda r: r.name == my_robot.name
    my_robots, other_robots = lib.partition(is_my_robot, field.robots.values())
    if len(my_robots) != 1:
        raise ValueError, "Robot name not found: %s" % my_robot_name
    my_robot = my_robots[0]
    gd = lambda struct, accept: lib.get_data_dict(struct, accept=accept)
    robot_gd = lambda struct: gd(struct, ["x", "y", "angle", "rotation", "shield", 
        "speed", "time_to_fire", "turret_angle", "turret_rotation"])
    data = {
        "id": str(field.battle_time),
        "time": field.battle_time,
        "robots": {
            "me": robot_gd(my_robot),
            "others": map(robot_gd, other_robots),
        },
        "bullets": [gd(bullet, ["x", "y", "angle", "speed"]) for bullet in field.bullets],
    }
    return yaml.dump(data, default_flow_style=False)                

def send_state(field, stream, robot):
    """Send field state to bot input stream."""
    data = get_state(field, robot)
    stream.write(data.rstrip() + "\n\n")
    stream.flush()

def get_input_callback(input_stream, output_stream):
    """Return a function callback to be called from main loop."""
    def _input_callback(loop_id, field, new_robot):
        send_state(field, input_stream, new_robot)
        while 1:
            line = output_stream.readline()
            spline = line.split()
            if not spline:
                continue
            update_id = spline[0]
            if update_id == str(field.battle_time) or update_id == "-":
                yield process_command(field, new_robot, spline[1:])
                if update_id[0] != "-":
                    break
    return _input_callback

def init(executable):
    """Start a process for the bot and return the subprocess.Popen object."""
    popen = subprocess.Popen(executable, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    return popen 

def process_command(field, new_robot, command):
    """Return new field for robot for a string line command."""
    def _run_command(spline, new_robot, new_bullets):
        command, args = spline[0], spline[1:]
        new_bullet = None
        if command == "set-speed":
            new_robot.speed = float(args[0])
            consumed = 2
        elif command == "set-rotation-speed":
            new_robot.rotation = float(args[0])
            consumed = 2
        elif command == "set-turret-rotation-speed":
            new_robot.turret_rotation = float(args[0])
            consumed = 2
        elif command == "fire":
            new_bullet = battlefield.fire_bullet(new_robot, field)
            new_bullets.append(new_bullet)
            consumed = 1
        elif command == "rotate-turret-to-angle-and-fire":
            if new_robot.time_to_fire:
                if new_robot.turret_final_angle is None:
                    new_robot.turret_final_angle = float(args[0])
            elif new_robot.fire_angle is None:
                new_robot.fire_angle = float(args[0])
            consumed = 2
        elif command == "rotate-turret-to-angle":
            if new_robot.turret_final_angle is None:
                new_robot.turret_final_angle = float(args[0])
            consumed = 2
        else:
            raise ValueError, "unknown command: %s" % command
        return consumed, new_robot, new_bullets
        
    new_bullets = []
    while command:
        try:
            consumed, new_robot, new_bullets = _run_command(command, new_robot, new_bullets)
            del command[:consumed]
        except ValueError, exc:
            lib.debug("command error: %s" % exc)
            break
    return battlefield.StateChange(update_robots=[new_robot], new_bullets=new_bullets)
