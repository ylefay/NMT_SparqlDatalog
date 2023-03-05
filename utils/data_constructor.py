import json
from utils import datalog_preprocessing, sparql_preprocessing

# Construct the data.{en,datalog} file.. used by nmt from json.

# Create the data files.
def create_data_files(DATASET_PATH, file_paths, json_db):
    with open(DATASET_PATH + file_paths[0], "w+") as file_en, open(
        DATASET_PATH + file_paths[1], "w+"
    ) as file_datalog, open(DATASET_PATH + file_paths[2], "w+") as file_sparql:
        possible_english_labels = [
            "intermediary_question",
            "corrected_question",
            "question",
        ]
        for label in possible_english_labels:
            if label in json_db[0].keys():
                q = label
                break
        for s in json_db:
            file_en.write(f"{s[q]}\n")
            file_datalog.write(f"{datalog_preprocessing(s['datalog_query'])}\n")
            file_sparql.write(f"{sparql_preprocessing(s['sparql_query'])}\n")


# for bert, br tags
def create_data_files_tags(DATASET_PATH, file_paths, json_db):

    with open(DATASET_PATH + file_paths[0], "w+") as file_bert, open(
        DATASET_PATH + file_paths[1], "w+"
    ) as file_br:
        for s in json_db:
            file_bert.write(f"{s['BERT_POS']}\n")
            file_br.write(f"{s['BR_TAGS']}\n")


if __name__ == "__main__":
    # For KB-simplified requests:
    DATASET_PATH = "../datasets/LC-QuAD/"
    DATASET_NAME = "LC-QuAD"
    DATASET_FILE = "KB_simplified_data-datalog.json"
    file_paths = [
        "data.en",
        "data.datalog",
        "data.sparql",
    ]
    json_db = json.load(open(DATASET_PATH + DATASET_FILE))
    create_data_files(DATASET_PATH, file_paths, json_db)
    # For BERT, BRACKET tags:
    DATASET_PATH = "../datasets/LC-QuAD/"
    DATASET_NAME = "LC-QuAD"
    DATASET_FILE = f"{DATASET_NAME}_bert_tag.json"
    file_paths = [
        "data.bert",
        "data.br",
    ]
    json_db = json.load(open(DATASET_PATH + DATASET_FILE))
    create_data_files_tags(DATASET_PATH, file_paths, json_db)
