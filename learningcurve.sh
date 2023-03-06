#!/usr/bin/env zsh
DATASET=$1
SRC_EXTENSION=$3
TGT_EXTENSION=$4
MODEL=$2
NUM_TRAIN_STEPS=$5
args=("$@")
for i in {6..${#args[@]}}
do
IFS=',' read TRAINING_PERCENTAGE TEST_PERCENTAGE <<< "${args[${i}]}"
sh generate.sh $DATASET $SRC_EXTENSION $TGT_EXTENSION $TRAINING_PERCENTAGE $TEST_PERCENTAGE
sh train.sh $DATASET ${MODEL}_{$TRAINING_PERCENTAGE}_{$TEST_PERCENTAGE} $NUM_TRAIN_STEPS $SRC_EXTENSION $TGT_EXTENSION
done