#!/bin/bash
python evaluation_manager.py 1 990 | tee output.txt &
wait
python evaluation_manager.py 2 990 | tee output2.txt &
wait
python evaluation_manager.py 3 990 | tee output3.txt &
wait
python evaluation_manager.py 4 990 | tee output4.txt &
wait
