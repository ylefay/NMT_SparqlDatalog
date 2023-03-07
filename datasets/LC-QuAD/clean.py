# Errors in the LC-QuAD database: a recurring case is:
# "corrected_question": "What is the allegiance of John Kotelawala ?",
# "intermediary_question": "What is the <allegiance> of John Kotelawala ?","
import json
import re

test = json.load(open("./original_json_files/test-data.json"))
train = json.load(open("./original_json_files/train-data.json"))
both = json.load(open("./original_json_files/data.json"))
dbs = [test, train, both]


def fix_1():
    for i, json_db in enumerate(dbs):
        for idx, s in enumerate(json_db):
            if (
                s["intermediary_question"].count("<") == 1
                and s["intermediary_question"].count(">") == 1
                and (
                    "What is the" in s["intermediary_question"]
                    or "Who is the" in s["intermediary_question"]
                    or "Who are the" in s["intermediary_question"]
                    or "What are the" in s["intermediary_question"]
                )
            ):
                splitted = re.split("(\>.+?\?)", s["intermediary_question"])
                splitted[-2] = "> of <" + splitted[-2][5:-2] + "> ?"
                s["intermediary_question"] = "".join(splitted)
            s["intermediary_question"] = re.sub(">+", ">", s["intermediary_question"])
            s["intermediary_question"] = re.sub("<+", "<", s["intermediary_question"])
            if (
                "What is the" in s["intermediary_question"]
                or "Who is the" in s["intermediary_question"]
                or "Who are the" in s["intermediary_question"]
                or "What are the" in s["intermediary_question"]
            ) and ("?" not in s["intermediary_question"]):
                s["intermediary_question"] += "?"
            dbs[i][idx] = s
    return dbs


if __name__ == "__main__":
    dbs = fix_1()
    test, train, both = dbs[0], dbs[1], dbs[2]
    with open("./test-data.json", "w+") as out_test, open(
        "./train-data.json", "w+"
    ) as out_train, open("./data.json", "w+") as out_both:
        out_test.write(json.dumps(test))
        out_train.write(json.dumps(train))
        out_both.write(json.dumps(both))
    json_db = json.load(open("./train-data-datalog.json"))
    for idx, s in enumerate(train):
        json_db[idx]["intermediary_question"] = s["intermediary_question"]
    with open("./train-data-datalog.json", "w+") as out_file:
        out_file.write(json.dumps(json_db))
