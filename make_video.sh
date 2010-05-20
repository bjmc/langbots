#!/bin/bash
export PYTHONPATH=. 
python langbots/main.py \
    -r robot1:commands:bots/python/simplebot.py \
    -r robot2:commands:bots/bash/simple.sh \
    -f 25 \
    -o video | ffmpeg -f image2pipe -i pipe:.jpeg -y -r 25 battle.avi
