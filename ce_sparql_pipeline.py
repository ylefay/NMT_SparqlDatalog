from POS_BR_tags.pos import drop_brackets
from utils.utils import levenshtein
import json
from pipeline import full_pipeline as _full_pipeline


def full_pipeline(ce_untagged_query):
    return _full_pipeline(
        ce_untagged_query,
        bert_br_MODEL_PATH=bert_br_MODEL_PATH,
        src_tgt_MODEL_PATH=src_tgt_MODEL_PATH,
        exceptions_for_replace=["SELECT", "DISTINCT", "COUNT", "WHERE"],
        src="en",
        tgt="sparql",
        silent=silent,
    )


def run_pipeline_on_db(OUTFILE_PATH, json_db):
    possible_english_labels = ["intermediary_question"]
    for label in possible_english_labels:
        if label in json_db[0].keys():
            english_label = label
    out_json = [{} for i in range(len(json_db))]
    for idx, s in enumerate(json_db):
        try:
            out_json[idx] = {
                "_id": s["_id"],
                english_label: drop_brackets(s[english_label]),
                "sparql_query": s["sparql_query"],
                "sparql_prev": full_pipeline(drop_brackets(s[english_label])),
            }
            out_json[idx].update(
                {
                    "dist": levenshtein(
                        out_json[idx]["sparql_prev"], out_json[idx]["sparql_query"]
                    )
                }
            )
        except:
            print(f"Exception:{s['_id']}")
    with open(OUTFILE_PATH, "w+") as out_file:
        out_file.write(json.dumps(out_json))


if __name__ == "__main__":
    N = 1
    DATASET_PATH = "./datasets/LC-QuAD/"
    DATASET_NAME = "LC-QuAD"
    DATASET_FILE = "data-datalog.json"
    OUTFILE_PATH = DATASET_NAME + "_OUTPUT_s.json"
    json_db = json.load(open(DATASET_PATH + DATASET_FILE))
    json_db = json_db[: min(N, len(json_db))]

    bert_br_MODEL_PATH = "./trained_models/LC-QuAD_bert_br"
    src_tgt_MODEL_PATH = "./trained_models/LC-QuAD_en_sparql"
    silent = False

    run_pipeline_on_db(OUTFILE_PATH, json_db)
    # ce_untagged_query = "What is the alumnus of of the fashion designer whose death place is Stony Brook University Hospital ?"
    # print(full_pipeline(ce_untagged_query))
    pass
