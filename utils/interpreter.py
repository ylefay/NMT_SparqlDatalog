#!/usr/bin/env python
"""

Neural SPARQL Machines - Interpreter module.

'SPARQL as a Foreign Language' by Tommaso Soru and Edgard Marx et al., SEMANTiCS 2017
https://arxiv.org/abs/1708.07624

Version 1.0.0

"""
import sys
import utils

if __name__ == "__main__":
    encoded_prevision = sys.argv[1]
    target_extension = sys.argv[2]
    # Inverse preprocessing
    if target_extension == "sparql":
        decoded_prevision = utils.sparql_invert_preprocessing(encoded_prevision)
    elif target_extension == "datalog":
        decoded_prevision = utils.datalog_invert_preprocessing(encoded_prevision)
    else:
        decoded_prevision = encoded_prevision
    print(decoded_prevision)
