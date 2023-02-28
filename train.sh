#!/usr/bin/env bash
#--tgt = datalog, sparql
SRC_EXTENSION=$4
TGT_EXTENSION=$5
DATASET=$1
MODEL=$2
NUM_TRAIN_STEPS=$3

mkdir ./$MODEL/
cp ./$DATASET/*.$SRC_EXTENSION ./$MODEL/
cp ./$DATASET/*.$TGT_EXTENSION ./$MODEL/
cd nmt
python -m nmt.nmt --src=$SRC_EXTENSION --tgt=$TGT_EXTENSION --vocab_prefix=../$MODEL/vocab --dev_prefix=../$MODEL/dev --test_prefix=../$MODEL/test --train_prefix=../$MODEL/train --out_dir=../$MODEL --num_train_steps=$NUM_TRAIN_STEPS --steps_per_stats=100 --num_layers=2 --num_units=128 --dropout=0.2 --metrics=bleu
cd ..
