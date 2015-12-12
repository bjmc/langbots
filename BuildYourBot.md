# Introduction #

**LangBots** allows the bots to be written in any language because the interface between the bot and the framework uses a universal interface: standard input and standard output.

# How it works #

  1. The bot is spawned with the configuration YAML file as first argument.
  1. The bot reads from standard input a succession of YAML structures, separated by an empty line. Each structure describe the state of the battlefield (robots and bullets) for a given time.
  1. For each read YAML the bot **MUST** respond with a command (writing a line to its standard output).

For more info about the YAML format, check the [Wikipedia page](http://en.wikipedia.org/wiki/YAML). YAML is a pretty ubiquitous format, all modern programming languages have parsing libraries.

## Example ##

If you want to see how a bot looks like, take a look to the example Python bot:

http://code.google.com/p/langbots/source/browse/#svn/trunk/bots/python

## Configuration ##

The config YAML given as first argument to the bot process has the following structure:

  * **robot**: Hash containing the following keys:
    * **type**: Type of the tank. For now, 'tank1', it may change for future versions.
    * **size**: `[width, height]` of the robot (pixels)
    * **shield**: Start value for the shield.
    * **max\_speed**: `[max_forward_speed, max_backward_speed]` (pixels/second)
    * **rotation\_max\_speed**: The maximum speed of the rotation of the robot (degrees/second).
    * **turret\_rotation\_max\_speed**: The maximum speed of the rotation of the turret (relative to the robot) (degrees/second).
    * **fire\_min\_interval**: Interval between consecutive bullets.
    * **bullet\_speed**: Speed of the bullets.
  * **map**: Hash containing the following keys:
    * **size**: `[width, height]` of the map (pixels).

Example:

```
robot:
  type: tank1
  size: [36, 38]
  shield: 5
  max_speed: [200.0, 100.0]
  rotation_max_speed: 100.0
  turret_rotation_max_speed: 125.0
  fire_min_interval: 0.5
  bullet_speed: 300.0     
     
map:
  size: [640, 480]
```

## Field input ##

**Langbots** sends info about the field in YAML format. The structure contains the following fields:

  * **id**: String identifier of the update. It will be used in the response command.
  * **time**: Time of simulation (seconds).
  * **robots**: Hash with two keys: _me_ (my robot) and _others_ (the other robots). Each robot is a map with the following keys:
    * **angle**: Angle of the robot (degrees) counter-clockwise. 0º is the robot looking to the right.
    * **rotation**: Rotation speed (degrees/second).
    * **shield**: Remaining shield (1 unit = 1 bullet impact). When reaches to zero the robot loses.
    * **x**: X-position (pixels). x=0 being the left side of the field.
    * **y**: Y-position (pixels). y=0 being the upper side of the field.
    * **speed**: Speed of the robot (pixels/second).
    * **time\_to\_fire**: How much time the robot has to wait till the gun is recharged and can fire again (that prevents the robot to send fire bursts).
    * **turret\_angle**: Angle of the turret relative to the robot position (degrees).
    * **turret\_rotation**: Speed of the turret rotation (degrees/second).
  * **bullets**: List of bullets. Each bullet is a hash with the following keys:
    * **x**: X-position (pixels).
    * **y**: Y-position (pixels).
    * **angle**: Angle of the direction of the bullet (degrees).
    * **speed**: Linear speed of the bullet (pixels /second).

Example:

```
id: '0.68'
time: 0.68000000000000005
robots:
  me:
    angle: 9.7199999999997999
    rotation: -59.0
    shield: 5
    speed: 138.0
    time_to_fire: 0.5
    turret_angle: 77.920000000000186
    turret_rotation: 0.0
    x: 446.59649044204843
    y: 76.726805725693964
  others:
  - angle: 20.399999999999807
    rotation: 30.0
    shield: 5
    speed: 200.0
    time_to_fire: 0.46000000000000002
    turret_angle: 72.000000000000171
    turret_rotation: 0.0
    x: 453.39071947435502
    y: 361.43864856050476
bullets:
- angle: 87.999999999999829
  speed: 300.0
  x: 439.94896488608407
  y: 317.23843688980429
- angle: 87.079999999999814
  speed: 300.0
  x: 443.10054148534948
  y: 40.597155007198523
```

## Commands ##

The bot writes the response to its standard output with the following syntax:

```
UPDATE-ID [COMMAND1 [ARG] [COMMAND2 [ARG] ...]
```

_UPDATE-ID_ is the identifier received from the YAML and it must be included in the command to make sure actions are synchronized.

The available commands are:

  * **set-speed** _SPEED_: Set robot speed, positive means forward, negative backwards. Examples: `set-speed 150`, `set-speed -40`.
  * **set-rotation-speed** _SPEED_: Set rotation speed. Positive means counter-clockwise, negative clockwise. Examples: `set-rotation-speed 90`.
  * **set-turret-rotation-speed** _SPEED_: Set turret rotation speed. Examples: `set-turret-rotation-speed 90`.
  * **fire**: Fire a bullet. The command will be ignored if time\_to\_fire is not 0.0.
  * **rotate-turret-to-angle-and-fire** _ANGLE_: When you write a bot you want to fire a bullet to a given angle. Doing so by using _set-turret-rotation-speed_ and _fire_ would be extremely tedious, so this command makes it very easy. Example: `rotate-turret-to-angle-and-fire 60.0`.

Example of command (responds to an update with id=1234):

```
1234 set-speed 40 set-rotation-speed -80 rotate-turret-to-angle-and-fire 45.0
```

Note that commands are executed in parallel, the order in which you write them is not important.

If you are initializing the robot you won't have an _update-id_, you then use "-" to indicate that the command is not bound to any update:

```
- set-speed 50
```

## Caveats ##

  * You must send **one and only one command** per update loop. Otherwise the framework will hang up (eventually, the bot will be disqualified)
  * Flush the channel after writing the command.