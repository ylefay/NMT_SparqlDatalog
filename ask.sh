#!/usr/bin/env bash
MODEL=$1
SRC_EXTENSION=$3
TGT_EXTENSION=$4

cd nmt
echo "$2" > to_ask.txt
python -m nmt.nmt  --vocab_prefix=../$MODEL/vocab --model_dir=../$MODEL  --inference_input_file=./to_ask.txt  --inference_output_file=./output.txt --out_dir=../$MODEL --src=$SRC_EXTENSION --tgt=$TGT_EXTENSION | tail -n4

if [ $? -eq 0 ]
then
    echo ""
    echo "ANSWER IN $TGT_EXTENSION SEQUENCE:"
    ENCODED="$(cat output.txt)"
    python ../utils/interpreter.py "${ENCODED}" $TGT_EXTENSION -- > output_decoded.txt
    cat output_decoded.txt
    echo ""
fi

cd ..
