#!/bin/bash
python experiment_manager.py 1 990 | tee output.txt &
wait
python experiment_manager.py 2 990 | tee output2.txt &
wait
python experiment_manager.py 3 990 | tee output3.txt &
wait
python experiment_manager.py 4 990 | tee output4.txt &
wait
python experiment_manager.py 5 991 | tee output5_100.txt &
wait