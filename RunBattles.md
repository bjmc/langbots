# Introduction #

You have started writing you own bot and you want to test it. You have now some options: make it fight against itself, make it fight against other bot or play with it interactive.

## Interactive battle ##

You have to instruct **LangBots** to use the bot for one robot and _pgyame_ input for the other:

```
langbots/main.py \
    -r robot1:commands:bots/python/simplebot.py \
    -r robot2:pygame \
    -o pygame
```

Keys are: _arrow keys_ (up=forward, down=backward, right=rotate right, left=rotate left), _A_ (rotate turret left), _X_ (rotate turret right), _C_ (fire).

## Dump a battle ##

```
langbots/main.py \
    -r robot1:commands:bot1.py \
    -r robot2:commands:bot2.rb \
    -o dump:bot1-bot2.dump -f 25
```

This will generate a file _bot1-bot2.dump_ with the battle. You can know play it on a Pygame window (see how you select the bot images to use):

```
langbots/main.py "$@" \
    -p simple-simple.dump
    -o pygame:robot1=blue1:robot2=red1
```

## Create a video ##

You can even generate a video of a battle so you can distribute it. You need [ffmpeg](http://www.ffmpeg.org/). For example this command will start a battle between _bot1.py_ and _bot2.rb_, and generate a video named _battle.avi_.

```
#!/bin/bash
langbots/main.py \
    -r robot1:commands:bot1.py \
    -r robot2:commands:bot2.rb \
    -f 25 \
    -o video | ffmpeg -f image2pipe -i pipe:.jpeg -y -r 25 battle.avi
```