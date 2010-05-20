#!/bin/bash
export PYTHONPATH=. python 
python langbots/main.py \
    -r robot1:commands:bots/python/simplebot.py \
    -r robot2:pygame \
    -o pygame
