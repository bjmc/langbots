#!/bin/bash
export PYTHONPATH=. 
python langbots/main.py "$@" \
    -r robot1:commands:bots/python/simplebot.py \
    -r robot2:commands:bots/python/simplebot.py \
    -o dump:simple-simple.dump -f 25
