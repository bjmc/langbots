#!/bin/bash
export PYTHONPATH=. 
python langbots/main.py "$@" \
    -p simple-simple.dump \
    -o pygame:robot1=blue1:robot2=red1
