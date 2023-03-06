#!/usr/bin/env python
"""

Neural SPARQL Machines - Split into train, dev, and test sets.

'SPARQL as a Foreign Language' by Tommaso Soru and Edgard Marx et al., SEMANTiCS 2017
https://arxiv.org/abs/1708.07624

Version 1.0.0

"""
import argparse
import random
import os
import io


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    requiredNamed = parser.add_argument_group("required named arguments")
    requiredNamed.add_argument(
        "--lines",
        dest="lines",
        metavar="lines",
        help="total number of lines (wc -l <file>)",
        required=True,
    )
    requiredNamed.add_argument(
        "--dataset",
        dest="dataset",
        metavar="dataset.sparql",
        help="sparql or datalog dataset file",
        required=True,
    )
    requiredNamed.add_argument(
        "--srcextension", dest="srcextension", help="en for example", required=True
    )
    requiredNamed.add_argument(
        "--tgtextension",
        dest="tgtextension",
        help="datalog or sparql for example",
        required=True,
    )
    requiredNamed.add_argument(
        "--trainingpercentage",
        dest="trainingpercentage",
        help="training percentage",
        default=80,
    )
    requiredNamed.add_argument(
        "--testpercentage",
        dest="testpercentage",
        help="test percentage",
        default=10,
    )
    args = parser.parse_args()
    TRAINING_PERCENTAGE = int(args.trainingpercentage)
    TEST_PERCENTAGE = int(args.testpercentage)
    DEV_PERCENTAGE = 100-TRAINING_PERCENTAGE-TEST_PERCENTAGE
    lines = int(args.lines)
    dataset_file = os.path.splitext(args.dataset)[0]
    tgtextension = args.tgtextension
    srcextension = args.srcextension
    tgt_file = f"{dataset_file}.{tgtextension}"
    src_file = f"{dataset_file}.{srcextension}"

    random.seed()

    test_and_dev_percentage = sum([TEST_PERCENTAGE, DEV_PERCENTAGE])
    number_of_test_and_dev_examples = int(lines * test_and_dev_percentage / 100)
    number_of_dev_examples = int(
        number_of_test_and_dev_examples * DEV_PERCENTAGE / test_and_dev_percentage
    )

    dev_and_test = random.sample(range(lines), number_of_test_and_dev_examples)
    dev = random.sample(dev_and_test, number_of_dev_examples)
    with io.open(tgt_file, encoding="utf-8") as original_tgt, io.open(
        src_file, encoding="utf-8"
    ) as original_src:
        tgt = original_tgt.readlines()
        src = original_src.readlines()

        dev_tgt_lines = []
        dev_src_lines = []
        train_tgt_lines = []
        train_src_lines = []
        test_tgt_lines = []
        test_src_lines = []

        for i in range(len(tgt)):
            tgt_line = tgt[i]
            src_line = src[i]
            if i in dev_and_test:
                if i in dev:
                    dev_tgt_lines.append(tgt_line)
                    dev_src_lines.append(src_line)
                else:
                    test_tgt_lines.append(tgt_line)
                    test_src_lines.append(src_line)
            else:
                train_tgt_lines.append(tgt_line)
                train_src_lines.append(src_line)

        with io.open(
            f"train.{tgtextension}", "w", encoding="utf-8"
        ) as train_tgt, io.open(
            f"train.{srcextension}", "w", encoding="utf-8"
        ) as train_src, io.open(
            f"dev.{tgtextension}", "w", encoding="utf-8"
        ) as dev_tgt, io.open(
            f"dev.{srcextension}", "w", encoding="utf-8"
        ) as dev_src, io.open(
            f"test.{tgtextension}", "w", encoding="utf-8"
        ) as test_tgt, io.open(
            f"test.{srcextension}", "w", encoding="utf-8"
        ) as test_src:

            train_tgt.writelines(train_tgt_lines)
            train_src.writelines(train_src_lines)
            dev_tgt.writelines(dev_tgt_lines)
            dev_src.writelines(dev_src_lines)
            test_tgt.writelines(test_tgt_lines)
            test_src.writelines(test_src_lines)
