import os
from POS_BR_tags.pos import br_tagging, pipeline, fix_pipeline, drop_brackets
from utils.utils import do_replacements, levenshtein, do_replacements_except
from utils.KB_simplification import simplify_english_request
import json
import tempfile


def full_pipeline(ce_untagged_query, silent=False):
    temp_file = tempfile.NamedTemporaryFile().name
    if not silent:
        print(f"Query: {ce_untagged_query}")

    # Tagging KB specific terms
    piped_query = fix_pipeline(pipeline(ce_untagged_query))
    bert_pos_tags = " ".join([el["entity"] for el in piped_query])
    if not silent:
        print(f"BERT_POS_TAGS: {bert_pos_tags}")
    os.system(
        f'./ask.sh ./trained_models/LC-QuAD_bert_br "{bert_pos_tags}" bert br > {temp_file}'
    )
    br_tags_file = open(f"{temp_file}", "r").read()
    br_tags = br_tags_file.split("\n")[-3]
    if not silent:
        print(f"BR TAGS: {br_tags}")
    os.remove(f"{temp_file}")
    ce_query = br_tagging(ce_untagged_query, piped_query, br_tags.split(" "))
    kb_simplified_query, mapping_replace = simplify_english_request(ce_query)
    if not silent:
        print(f"KBs Query: {kb_simplified_query}")

    # Use NMT model to translate the KB-simplified CE english request to KB-simplified Datalog request
    os.system(
        f'./ask.sh ./trained_models/LC-QuAD_en_sparql "{kb_simplified_query}" en sparql > {temp_file}'
    )
    datalog_file = open(f"{temp_file}", "r").read()
    os.remove(f"{temp_file}")
    datalog_query = datalog_file.split("\n")[-3]
    # Replace back
    mapping_replace = {
        mapping_replace[key]: do_replacements(key, {" ": "_"})
        for key in mapping_replace.keys()
    }
    print(mapping_replace)
    datalog_query = do_replacements_except(
        datalog_query, mapping_replace, " ", ["SELECT", "DISTINCT", "COUNT", "WHERE"]
    )

    if not silent:
        print(f"Prev. datalog query: {datalog_query}")
    return datalog_query


def run_pipeline_on_db(OUTPUT_FILE, json_db):
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
                "sparql_prev": full_pipeline(
                    drop_brackets(s[english_label]), silent=False
                ),
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
    with open(OUTPUT_FILE, "w+") as out_file:
        out_file.write(json.dumps(out_json))


if __name__ == "__main__":
    N = 200
    DATASET_PATH = "./datasets/LC-QuAD/"
    DATASET_NAME = "LC-QuAD"
    DATASET_FILE = "data-datalog.json"
    OUTPUT_FILE = DATASET_NAME + "_OUTPUT_s.json"
    json_db = json.load(open(DATASET_PATH + DATASET_FILE))
    json_db = json_db[: min(N, len(json_db))]
    run_pipeline_on_db(OUTPUT_FILE, json_db)
    # ce_untagged_query = "What is the alumnus of of the fashion designer whose death place is Stony Brook University Hospital ?"
    # print(full_pipeline(ce_untagged_query))
    pass
