#!/usr/bin/python
import pygame

# App modules
from langbots import lib
from langbots import battlefield

# We need a global variable to hold the events for a loop. It will be set only 
# by the first callback, otherwise the events in the queue would be removed 
# and all subsequent callbacks would see no events. 
loop_events = {}

KeyboardControls = lib.struct("KeyboardControls", 
    ["forward", "backward", "rotate_right", "rotate_left", 
     "turret_rotate_right", "turret_rotate_left", "fire"]) 
     
def process_default_events(events): 
    """Respond to Pygame events."""
    for event in events:
        if event.type == pygame.QUIT: 
            return False              
    return True

def get_input_callback(controls, first=False):
    """Get input callback."""
    def _callback(loop_id, field, new_robot):        
        return input_callback(loop_id, field, new_robot, controls, first)
    return _callback
    
def input_callback(loop_id, field, new_robot, controls, first):
    """Process input keyboard events to move and rotate the robot."""
    # Use the same global events variables for all callbacks for a given loop.
    global loop_events
    #assert events is not None or first, "First callback must get events"""
    if loop_id not in loop_events:
        # Only the first callback on the loop has to get the events
        events = pygame.event.get()
        loop_events[loop_id] = events
    else:
        events = loop_events[loop_id]
    if not process_default_events(events):
        raise battlefield.AbortBattle
    
    new_bullet = None    
    changed = False
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == controls.fire:
                new_bullet = battlefield.fire_bullet(new_robot, field)
                changed = True
        def sign(x):
            return cmp(x, 0.0) or 1.0
        pressed = pygame.key.get_pressed()
        new_speed = new_rotation = new_turret_rotation = 0.0
        if pressed[controls.forward]:
            new_speed += 150
        if pressed[controls.backward]:
            new_speed += -100
        if pressed[controls.rotate_right]:
            new_rotation += -100*sign(new_speed)
        if pressed[controls.rotate_left]:
            new_rotation += 100*sign(new_speed)
        if pressed[controls.turret_rotate_left]:
            new_turret_rotation += 100
        if pressed[controls.turret_rotate_right]:
            new_turret_rotation += -100
        for attr, value in [("speed", new_speed), 
         ("rotation", new_rotation), 
         ("turret_rotation", new_turret_rotation)]:
             if getattr(new_robot, attr) != value:
                setattr(new_robot, attr, value)
                changed = True
    if changed:
        return [battlefield.StateChange(update_robots=[new_robot], 
            new_bullets=lib.compact([new_bullet]))]
