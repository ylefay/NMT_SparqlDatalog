#!/usr/bin/env python
"""

Neural SPARQL Machines - Interpreter module.

'SPARQL as a Foreign Language' by Tommaso Soru and Edgard Marx et al., SEMANTiCS 2017
https://arxiv.org/abs/1708.07624

Version 1.0.0

"""
import sys
from .utils import datalog_invert_preprocessing, sparql_invert_preprocessing
if __name__ == '__main__':
    encoded_prevision = sys.argv[1]
    target_extension = sys.argv[2] if len(sys.argv) >= 2 else 'sparql'
    #Inverse preprocessing
    if target_extension=='sparql':
        #decoded_prevision = fix_URI(decode(encoded_prevision))
        decoded_prevision = sparql_invert_preprocessing(encoded_prevision)
    elif target_extension=='datalog':
        decoded_prevision = datalog_invert_preprocessing(encoded_prevision)
    else:
        decoded_prevision = encoded_prevision
    print(decoded_prevision)
