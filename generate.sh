#!/usr/bin/env bash
DATASET=$1
SRC_EXTENSION=$2
TGT_EXTENSION=$3
if [ "$4" ] & [ "$5" ]; then
    TRAINING_PERCENTAGE=$4
    TEST_PERCENTAGE=$5
else
    TRAINING_PERCENTAGE=80
    TEST_PERCENTAGE=10
fi
echo "Building $SRC_EXTENSION vocabulary..."
python utils/build_vocab.py ${DATASET}/data.$SRC_EXTENSION > ${DATASET}/vocab.$SRC_EXTENSION
echo "Building $TGT_EXTENSION vocabulary..."
python utils/build_vocab.py ${DATASET}/data.$TGT_EXTENSION > ${DATASET}/vocab.$TGT_EXTENSION

NUM_LINES=$(echo awk '{ print $1}' | cat ${DATASET}/data.$TGT_EXTENSION | wc -l)

NSPM_HOME=`pwd`
cd ${DATASET}
echo "Splitting data into train, dev, and test sets..."
python ${NSPM_HOME}/utils/split_in_train_dev_test.py --lines $NUM_LINES --dataset data.$TGT_EXTENSION --srcextension $SRC_EXTENSION --tgtextension $TGT_EXTENSION --trainingpercentage $TRAINING_PERCENTAGE --testpercentage $TEST_PERCENTAGE
cd ${NSPM_HOME}
echo "Done."