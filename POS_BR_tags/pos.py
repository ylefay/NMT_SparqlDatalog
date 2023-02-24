# Construct (BERT POS tags, bracket tags) database for the LC-QuAD database

from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    TokenClassificationPipeline,
)
import json
import re

model_name = "QCRI/bert-base-multilingual-cased-pos-english"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)

pipeline = TokenClassificationPipeline(model=model, tokenizer=tokenizer)


def drop_brackets(query: str):
    return query.replace("<", "").replace(">", "")


# function to fix pipeline: idk why it splits some words into different part with ## and same entity
def fix_pipeline(piped_query):
    fixed_piped_query = []
    for idx in range(len(piped_query)):
        if len(piped_query[idx]["word"]) > 1:
            if piped_query[idx]["word"][:2] == "##":
                fixed_piped_query[-1]["word"] += piped_query[idx]["word"][2:]
                fixed_piped_query[-1]["end"] = piped_query[idx]["end"]
            else:
                fixed_piped_query.append(piped_query[idx])
        else:
            fixed_piped_query.append(piped_query[idx])
    return fixed_piped_query


def br_tags(tagged_query: str, piped_query):
    splitted = re.split("(\<.+?\>)", tagged_query)

    def get_position(splitted, start):  # not optimal
        n = -1
        L = 0
        while L <= start:
            n += 1
            L += len(splitted[n])
        return n

    def shift_pos(splitted, pos, pos_in_split):
        if pos_in_split != 0:
            return pos - sum([len(x) for x in splitted[:pos_in_split]])
        return pos

    def tag(split, start_p, end_p):
        if not (split[0] == "<"):
            return "N"
        else:
            if split[start_p - 1] == "<" and split[end_p] == ">":
                return "B"
            if split[start_p - 1] == "<" and split[end_p] != ">":
                return "O"
            if split[start_p - 1] != "<" and split[end_p] == ">":
                return "E"
            return "I"

    piped_query_p = filter(lambda x: x["word"] not in {"<", ">"}, piped_query)
    tags = []
    for el_of_pipe in piped_query_p:
        start = el_of_pipe["start"]
        end = el_of_pipe["end"]
        pos_in_split = get_position(splitted, start)
        start_p = shift_pos(splitted, start, pos_in_split)
        end_p = shift_pos(splitted, end, pos_in_split)
        tags.append(tag(splitted[pos_in_split], start_p, end_p))
    return tags


def br_tagging(untagged_query: str, piped_untagged_query, tags):
    shift = 0
    tagged_query = untagged_query
    for idx, el_of_pipe in enumerate(piped_untagged_query):
        tag = tags[idx]
        start = el_of_pipe["start"]
        end = el_of_pipe["end"]
        if tag == "B":
            tagged_query = (
                tagged_query[: start + shift]
                + "<"
                + tagged_query[start + shift : end + shift]
                + ">"
                + tagged_query[end + shift :]
            )
            shift += 2
        elif tag == "O":
            tagged_query = (
                tagged_query[: start + shift] + "<" + tagged_query[start + shift :]
            )
            shift += 1
        elif tag == "E":
            tagged_query = (
                tagged_query[: end + shift] + ">" + tagged_query[end + shift :]
            )
            shift += 1
    return tagged_query


def create_bert_tag_database(DATASET_PATH, DATASET_NAME, json_db):
    out_training_db = [{} for i in range(len(json_db))]
    for idx, s in enumerate(json_db):
        piped_query = fix_pipeline(pipeline((s["intermediary_question"])))
        piped_query_without_brackets = fix_pipeline(
            pipeline(drop_brackets(s["intermediary_question"]))
        )
        out_training_db[idx]["BERT_POS"] = " ".join(
            [el_of_pipe["entity"] for el_of_pipe in piped_query_without_brackets]
        )
        out_training_db[idx]["BR_TAGS"] = " ".join(
            br_tags((s["intermediary_question"]), piped_query)
        )
        out_training_db[idx]["intermediary_question"] = s["intermediary_question"]
        out_training_db[idx]["_id"] = s["_id"]
    with open(f"{DATASET_PATH}/{DATASET_NAME}_bert_tag.json", "w+") as outfile:
        outfile.write(json.dumps(out_training_db))


if __name__ == "__main__":

    # Data sources
    DATASET_PATH = "../datasets/LC-QuAD/"
    DATASET_NAME = "LC-QuAD"
    DATASET_FILE = "train-data-datalog.json"

    N = 100000  # restricting the db
    json_db = json.load(open(DATASET_PATH + DATASET_FILE))
    json_db = json_db[: min(len(json_db), N)]
    create_bert_tag_database(DATASET_PATH, DATASET_NAME, json_db)

    # s = "What is the alumnus of of the fashion designer whose death place is Stony Brook University Hospital ?"
    # end_s = "What is the <alumnus of> of the <fashion designer> whose <death place> is <Stony Brook University Hospital> ?"
    # tags = "N N N O E N N O E N O E N O I I E N"
    # print(br_tagging(s, fix_pipeline(pipeline(s)), tags.split(' ')))

    pass
