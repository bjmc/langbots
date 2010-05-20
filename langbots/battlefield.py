#!/usr/bin/python
import time
import math
import itertools

import yaml

# App modules
from langbots import lib
from langbots import geometry

# Define struct types (using a class wrapper)
Field = lib.struct("Field", ["config", "robots", "bullets", "battle_time"])
Robot = lib.struct("Robot", ["name", "x", "y", "width", "height", "speed", 
                             "rotation", "angle", "turret_rotation", 
                             "turret_angle", "shield", "time_to_fire", 
                             "fire_angle", "turret_final_angle"])
Bullet = lib.struct("Bullet", ["x", "y", "angle", "speed", "origin"])
StateChange = lib.struct("StateChange", ["update_robots", "new_bullets"])

class AbortBattle(Exception):
    pass

def add_yaml_representers():
    def _object_representer(dumper, data):    
        mapping = dict((k, getattr(data, k)) for k in data.__slots__)
        return dumper.represent_mapping(data.__class__.__name__, mapping)
    yaml.add_representer(Field, _object_representer)
    yaml.add_representer(Robot, _object_representer)
    yaml.add_representer(Bullet, _object_representer)

def add_yaml_constructors():
    def object_constructor(loader, node):
        mapping = loader.construct_mapping(node)
        return globals()[node.tag](**mapping)
    yaml.add_constructor(u'Field', object_constructor)
    yaml.add_constructor(u'Robot', object_constructor)
    yaml.add_constructor(u'Bullet', object_constructor)

def read_yaml_block(stream):
    yamldata = itertools.takewhile(lambda s: s.strip(), stream)
    return yaml.load("".join(yamldata))

def create_robot(**kwargs):
    default = dict(x=0.0, y=0.0, speed=0.0, rotation=0.0, angle=0.0, 
        turret_angle=0.0, turret_rotation=0.0, shield=1, 
        time_to_fire=0.0, fire_angle=None, turret_final_angle=None)
    return Robot(**dict(default, **kwargs))

def get_polygon_for_robot(robot):
    """Get exact polygon (points) of robot with rotation.""" 
    w2 = robot.width / 2.0
    h2 = robot.height / 2.0
    alpha = geometry.torad(-robot.angle)
    dx2 = (w2*math.cos(alpha), -w2*math.sin(-alpha)) 
    dy2 = (h2*math.sin(-alpha), h2*math.cos(alpha))
    center = (robot.x, robot.y)
    p1 = geometry.sum_vectors([center, geometry.invert_vector(dx2), 
        geometry.invert_vector(dy2)])
    p2 = geometry.sum_vectors([center, geometry.invert_vector(dx2), dy2])
    p3 = geometry.sum_vectors([center, dx2, dy2])
    p4 = geometry.sum_vectors([center, dx2, geometry.invert_vector(dy2)])
    return [p1, p2, p3, p4]

def fire_bullet(robot, field):
    """Create a bullet for robot with a given speed and add it field.bullets."""
    if robot.time_to_fire:
        return
    absolute_angle = robot.angle + robot.turret_angle
    turret_length = robot.height / 1.5
    x = robot.x + turret_length * math.cos(geometry.torad(absolute_angle))
    y = robot.y - turret_length * math.sin(geometry.torad(absolute_angle))
    bullet = Bullet(x=x, y=y, angle=absolute_angle, origin=robot.name,
        speed=field.config["robot"]["bullet_speed"])
    return bullet

def check_bullet_collision(robots, bullet):
    """Return robot that collides with bullet (None if no collision)."""
    for robot in robots:
        if bullet.origin == robot.name:
            continue            
        polygon = get_polygon_for_robot(robot)
        if geometry.check_point_in_polygon((bullet.x, bullet.y), polygon):
            #lib.debug("collision: %s - %s" % (bullet, robot))
            return robot 

def process_robot(robot, dt, screen_size):
    """Get new robot position and rotation attributes for a time-delta."""
    new_robot = lib.clone_struct(robot)
    screen_width, screen_height = screen_size            
    body_width, body_height = robot.width, robot.height
    new_robot.x = robot.x + dt * robot.speed * math.cos(geometry.torad(robot.angle))
    if new_robot.x - body_width/2.0 < 0:
        new_robot.x = body_width/2.0
    elif new_robot.x + body_width/2.0 >= screen_width:
        new_robot.x = screen_width - body_width/2.0
    new_robot.y = robot.y - dt * robot.speed * math.sin(geometry.torad(robot.angle))
    if new_robot.y < body_height/2.0:
        new_robot.y = body_height/2.0
    elif new_robot.y + body_height/2.0 >= screen_height:
        new_robot.y = screen_height - body_height/2.0                
    new_robot.angle = geometry.normalize_angle(robot.angle + dt * robot.rotation)    
    return new_robot

def process_turret(field, robot, dt):
    """Get new turret position and rotation attributes for a time-delta."""
    new_robot = lib.clone_struct(robot)
    move_to_angle = lib.first([robot.fire_angle, robot.turret_final_angle], 
        pred=lambda x: x is not None)
    new_bullets = []    
    new_turret_angle = robot.turret_angle + dt * robot.turret_rotation
    if move_to_angle is not None:
        old_direction = geometry.get_direction_for_rotation(
            robot.angle + robot.turret_angle, move_to_angle)
        new_direction = geometry.get_direction_for_rotation(
            robot.angle + new_turret_angle, move_to_angle)
        if old_direction * new_direction < 0:
            new_robot.turret_rotation = 0.0
            if robot.fire_angle:
                new_bullet = fire_bullet(robot, field)
                new_bullets.append(new_bullet)
            new_turret_angle = move_to_angle - robot.angle
            new_robot.fire_angle = None
            new_robot.turret_final_angle = None
        else:
            max_speed = field.config["robot"]["turret_rotation_max_speed"]
            new_robot.turret_rotation = max_speed * new_direction
    else: 
        new_bullets = []
    new_robot.turret_angle = geometry.normalize_angle(new_turret_angle)

    # Update time to fire
    if robot.time_to_fire: 
        new_robot.time_to_fire -= dt
        if new_robot.time_to_fire < 0:
            new_robot.time_to_fire = 0.0                
    
    return StateChange(update_robots=[new_robot], new_bullets=new_bullets)

def find_collision(robots):
    """Return first collision between robots."""
    for robot1, robot2 in itertools.combinations(robots, 2):
        polygon1 = get_polygon_for_robot(robot1)
        polygon2 = get_polygon_for_robot(robot2)
        if geometry.check_collision_of_polygons(polygon1, polygon2):
            return robot1, robot2

def process_bullet(bullet, dt, screen_size):
    """Update bullet position for a delta_t."""
    new_bullet = lib.clone_struct(bullet)
    screen_width, screen_height = screen_size
    k = dt * bullet.speed
    new_bullet.x = bullet.x + k * math.cos(geometry.torad(bullet.angle))
    new_bullet.y = bullet.y - k * math.sin(geometry.torad(bullet.angle))
    if (new_bullet.x >= 0 and new_bullet.x < screen_width and
            new_bullet.y >= 0 and new_bullet.y < screen_height):
        return new_bullet

def apply_limits(robot, robot_config):
    """Fix limits in robot set in robot_config dictionary."""
    rc = robot_config
    max_forward, max_backward = rc["max_speed"]
    robot.speed = min(robot.speed, max_forward)
    robot.speed = max(robot.speed, -max_backward)
    robot.rotation = min(robot.rotation, rc["rotation_max_speed"])
    robot.rotation = max(robot.rotation, -rc["rotation_max_speed"])
    max_fire_rot = rc["turret_rotation_max_speed"]
    robot.turret_rotation = min(robot.turret_rotation, max_fire_rot)
    robot.turret_rotation = max(robot.turret_rotation, -max_fire_rot)
    return robot

def move_robots_and_process_collisions(robots, dt, map_size):
    """Return a StateChange object with new robots position and collisions resolved."""
    changes = dict((process_robot(robot, dt, map_size), robot) 
                   for robot in robots.values())
    while changes:
        robots = find_collision(changes.keys())
        if not robots:
            break
        # Robots collisions should not be frequent, so we can solve it
        # with a simple algorith: when two robots collide try to guess
        # the culprit (using the previous position) and discard its changes.  
        new_robot1, new_robot2 = robots
        if not find_collision([new_robot1, changes[new_robot2]]):
            del changes[new_robot2]                
        elif not find_collision([changes[new_robot1], new_robot2]):
            del changes[new_robot1]
        else: # we must discard both changes to resolve the collision                    
            del changes[new_robot1]
            del changes[new_robot2]
    return StateChange(update_robots=changes.keys(), new_bullets=[])

def apply_state_change(field, state_change):
    """UPDATE: Apply state changes to field.robots and field.bullets."""
    if not state_change:
        return
    for new_robot in state_change.update_robots:
        #assert new_robot.name == robot_name
        field.robots[new_robot.name] = \
            apply_limits(new_robot, field.config["robot"]) 
    for bullet in state_change.new_bullets:
        if bullet:
            field.bullets.append(bullet) 
            field.robots[bullet.origin].time_to_fire = \
                field.config["robot"]["fire_min_interval"]
      
def play(battle_stream, draw_callbacks):
    """Replay a saved battle."""
    itime = time.time()
    def get_battle_time():
        return time.time() - itime
    while 1:
        field = read_yaml_block(battle_stream)
        if not field:
            break
        while field.battle_time > get_battle_time():
            time.sleep(0.005)
        for draw_callback in draw_callbacks:
            draw_callback(field)

# This is the only "impure" function allowed to change state of field 
def run(field, input_callbacks, draw_callbacks, delta_time=None):
    """
    Run main battlefield loop: input + update + draw callbacks.
    
    Return the robot which won the battle (may be None). 
    """
    battle_start = time.time()
    itime = battle_start
    map_size = field.config["map"]["size"]
    field.battle_time = 0.0
    
    while len(field.robots) > 1:
        # Draw
        for draw_callback in draw_callbacks:
            draw_callback(field)
        
        ### Input         
        for robot_name, input_callback in input_callbacks.iteritems():
            if robot_name in field.robots:
                robot = field.robots[robot_name]
                state_changes = input_callback(itime, field, robot)
                for state_change in (state_changes or []):
                    apply_state_change(field, state_change)

        ### Update                
        if delta_time:
            dt = delta_time
            field.battle_time += dt
        else:
            new_time = time.time()
            dt, itime = (new_time - itime), new_time
            field.battle_time = new_time - battle_start

        # Update turrets
        for robot in field.robots.itervalues():
            state_changes = process_turret(field, robot, dt)
            apply_state_change(field, state_changes)
                            
        # Update bullets
        field.bullets = lib.compact(process_bullet(bullet, dt, map_size)
            for bullet in field.bullets)
                            
        # Update position of robots with control of collisions
        state_change = move_robots_and_process_collisions(field.robots, dt, map_size)
        apply_state_change(field, state_change)
                  
        # Check collision between bullets and robots
        def _get_collisions():
            for bullet in field.bullets:
                robot = check_bullet_collision(field.robots.values(), bullet)
                if robot:
                    yield (bullet, robot)
        collisions = dict(_get_collisions())
        for bullet, robot in collisions.iteritems():
            robot.shield -= 1
            if robot.shield <= 0: 
                # Robot is dead
                del field.robots[robot.name]
        field.bullets = lib.remove_from_list(field.bullets, collisions.keys())
            
    return field.robots and field.robots.values()[0]
