#!/bin/bash

python download.py $1 $2
python downloadFirstSubLevel.py $1 $2
python downloadSecondSubLevel.py $1 $2

cat resultUnique*.txt | sort | uniq > resultUniqueAll.txt