#!/bin/bash
python evalutation_manager 1 6 | tee output.txt &
wait
#python evalutation_manager 2 990 | tee output.txt &