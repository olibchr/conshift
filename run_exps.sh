#!/bin/bash
python evaluation_manager.py 1 6 | tee output.txt &
wait
#python evaluation_manager.py 2 990 | tee output.txt &