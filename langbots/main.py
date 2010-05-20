#!/usr/bin/python
import sys
import time
import optparse
import random

# Third-party modules
import yaml

# App modules
from langbots import lib
from langbots import battlefield
from langbots.inputmods import pygame_input, commands_input
from langbots.outputmods import pygame_output, dump_output

def init_robots(config_file, config, robot_options):
    input_callbacks = {}
    robots = {}
    screen_size = screen_width, screen_height = config["map"]["size"]
    robot_width, robot_height = config["robot"]["size"]
    default_positions = [
        (screen_width / 2.0, screen_height / 5.0),
        (screen_width / 2.0, 4*screen_height / 5.0),
    ]
    
    for robot_index, s in enumerate(robot_options):
        spline = s.split(":")
        robot_name, inputmod, modargs = spline[0], spline[1], spline[2:]
        x, y = default_positions[robot_index]
        robot = battlefield.create_robot(name=robot_name, x=x, y=y, 
            shield=config["robot"]["shield"], width=robot_width, height=robot_height)
        if inputmod == "commands":
            executable = modargs[0]
            bot = commands_input.init([executable, config_file])
            input_callback = commands_input.get_input_callback(bot.stdin, bot.stdout)
        elif inputmod == "pygame":
            import pygame
            controls1 = pygame_input.KeyboardControls(
                forward=pygame.K_UP, backward=pygame.K_DOWN, 
                rotate_right=pygame.K_RIGHT, rotate_left=pygame.K_LEFT,
                turret_rotate_right=pygame.K_x, turret_rotate_left=pygame.K_z,
                fire=pygame.K_c)
            input_callback = pygame_input.get_input_callback(controls1)
        else:
            raise ValueError, "input module not available: %s" % inputmod
        robots[robot.name] = robot
        input_callbacks[robot.name] = input_callback
    field = battlefield.Field(battle_time=0.0, config=config, robots=robots, bullets=[])
    return field, input_callbacks

def get_output_callbacks(field, output_options):
    output_callbacks = []
    screen_width, screen_height = field.config["map"]["size"]
    screen_size = screen_width, screen_height 
    robot_width, robot_height = field.config["robot"]["size"]
    bullet_speed = field.config["robot"]["bullet_speed"]

    for s in output_options:        
        spline = s.split(":")
        outputmod, args = spline[0], spline[1:]
        if outputmod == "pygame" or outputmod == "video":
            # example: pygame:robot1=blue4:robot2=red3            
            default_images = ["blue1", "red1"]
            robot_images = dict(s.split("=") for s in args)
            non_assigned = [robot_name for robot_name in field.robots 
                if robot_name not in robot_images]
            missing_images = dict((robot_name, default_images[index % len(default_images)]) 
                for (index, robot_name) in enumerate(non_assigned))
            robot_images.update(**missing_images)
            video = (outputmod == "video")
            screen, surfaces = pygame_output.init(screen_size, robot_images, video)
            output_callback = pygame_output.get_output_callback(screen, surfaces, video)
        elif outputmod == "dump":            
            basename = args[0]
            output_callback = dump_output.get_output_callback(field, basename)        
        else:
            raise ValueError, "output module not available: %s" % outputmod
        output_callbacks.append(output_callback)
    return output_callbacks    


def main(args):    
    """Init the battle field and start the main loop."""
    usage = """usage: %prog [OPTIONS]
    
    Start a Language Wars battle field""" 
    parser = optparse.OptionParser(usage)
    parser.add_option('-r', '--robot', dest='robot', action="append",
        default=[], help='Add a robot to the battlefield (name:pygame | name:commands:botpath)')
    parser.add_option('-o', '--output', dest='output', action="append",
        default=[], help='Active output module (pygame | dump:filename)')
    parser.add_option('-f', '--framerate', dest='frame_rate', type="int",
        default=None, help='Force framerate (for non-interactive)')
    parser.add_option('-p', '--play-battle', dest='play_battle', 
        default=None, help='Dump file to play')
    parser.add_option('-c', '--field-config-file', dest='config_file', 
        default=None, help='Path to YAML config file')
    options, args0 = parser.parse_args(args)
    
    config_file = options.config_file or "config/field.yml"
    config = yaml.load(open(config_file).read())
    battlefield.add_yaml_constructors()
    battlefield.add_yaml_representers()

    if options.play_battle:
        dump = open(options.play_battle)
        field = battlefield.read_yaml_block(dump)
    else:
        field, input_callbacks = init_robots(config_file, config, options.robot)
        
    output_callbacks = get_output_callbacks(field, options.output)            
     
    if options.play_battle:
        battlefield.play(dump, output_callbacks)
        return
    
    if not field.robots:
        parser.print_help()
        return 2
    elif len(field.robots) < 2:
        lib.error("Need at least 2 robots to fight")
        return 1    
    
    delta = (1.0 / options.frame_rate if options.frame_rate else None)        
    try:
        start_time = time.time()
        lib.debug("Start battle (%d robots: %s)" % 
            (len(field.robots), ", ".join(field.robots))) 
        winner = battlefield.run(field, input_callbacks, output_callbacks, delta)
        battle_time = time.time() - start_time
        print "winner: %s (%s)" % (winner.name, battle_time)
    except battlefield.AbortBattle:
        lib.error("Battle aborted")
        return 1
        
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
