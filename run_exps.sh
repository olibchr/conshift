#!/bin/bash
# Experiment 1: Run fixed time bins
python experiment_manager.py 1 990 | tee output.txt &
wait
# Experiment 2: Run flex time bins
python experiment_manager.py 2 990 | tee output2.txt &
wait
# Experiment 3: no tfidf
python experiment_manager.py 3 990 | tee output3.txt &
wait
# Experiment 1: Run flex time bins, kl divergence
python experiment_manager.py 4 990 | tee output4.txt &
wait
# Experiment 5: All previous runs with time bins if 52 or 100 as specified in the code (must be changed in lines 51,113-116 in experiment manager to either 52 or 100 as desired)
python experiment_manager.py 5 991 | tee output5_100.txt &
wait