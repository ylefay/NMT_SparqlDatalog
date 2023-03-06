import json
import numpy as np
if __name__ == "__main__":
    N = 200
    DATASET_PATH = "./LC-QuAD_OUTPUT.json"
    json_db = json.load(open(DATASET_PATH))
    json_db = json_db[: min(N, len(json_db))] 
    possible_fields = ['datalog_prev', 'sparqll_prev']
    for field in possible_fields:
        if field in json_db[0].keys():
            break
    print(np.mean([s['dist']/len(s[field]) for s in json_db if 'dist' in s.keys()]),np.std([s['dist']/len(s[field]) for s in json_db if 'dist' in s.keys()]))
    # ce_untagged_query = "What is the alumnus of of the fashion designer whose death place is Stony Brook University Hospital ?"
    # print(full_pipeline(ce_untagged_query))
    pass
