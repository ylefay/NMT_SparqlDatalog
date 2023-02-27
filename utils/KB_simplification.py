from utils import levenshtein, do_replacements
import json
import re


# specify to which domain the Kb specific term belongs
# from sparql query
def create_mapping(query):
    urls = [u[1:-1] for u in re.split("(\<.+?\>)", query) if u.startswith("<http")]
    urls_quotient = {"ontology": {}, "resource": {}, "property": {}}
    for url in urls:
        for k in urls_quotient.keys():
            if f"/{k}/" in url:
                urls_quotient[k][url] = url.split("/")[-1]
    mapping = {}
    for k in urls_quotient.keys():
        for obj in urls_quotient[k]:
            if obj not in mapping.keys():
                mapping[obj] = f"db{k[0]}_{chr(65+len(mapping.keys()))}"
    return mapping


# do not specify to which domain the kb specific term belongs
# from english query


def blind_create_mapping(query):
    kb_specific_terms = [
        u[1:-1] for u in re.split("(\<.+?\>)", query) if len(u) > 0 and u[0] == "<"
    ]
    mapping = {}
    for term in kb_specific_terms:
        if term not in mapping.keys():
            mapping[term] = f"{chr(65+len(mapping.keys()))}"
    return mapping


def eng(query, mapping):
    terms = [u[1:-1] for u in re.split("(\<.+?\>)", query) if u.startswith("<")]
    mapping_replace = {}
    for term in terms:
        _lev = {_obj: levenshtein(term, _obj) for _obj in mapping.keys()}
        obj = min(_lev, key=_lev.get)
        mapping_replace[term] = mapping[obj]
    query = do_replacements(query, mapping_replace)
    return query, mapping_replace


def sparql(query, mapping):
    query = do_replacements(query, mapping)
    return query


def datalog(query, mapping):
    query = do_replacements(query, mapping)
    return query


def blind_sparql(query, mapping):
    urls_quotient = {"ontology": {}, "resource": {}, "property": {}}
    mapping_replace = {}
    for field in urls_quotient.keys():
        urls_quotient[field] = [
            u[1:-1]
            for u in re.split("(\<.+?\>)", query)
            if u.startswith(
                (f"<http://dbpedia.org/{field}", f"<https://dbpedia.org/{field}")
            )
        ]
    for field in urls_quotient.keys():
        for url in urls_quotient[field]:
            _url = url.split("/")[-1]
            _lev = {_term: levenshtein(_term, _url) for _term in mapping.keys()}
            term = min(_lev, key=_lev.get)
            mapping_replace[url] = f"db{field[0]}_{mapping[term]}"
    query = do_replacements(query, mapping_replace)
    return query, mapping_replace


def blind_datalog(query, mapping):
    urls_quotient = {"ontology": [], "resource": [], "property": []}
    mapping_replace = {}
    for field in urls_quotient.keys():
        urls_quotient[field] = [
            u[1:-1]
            for u in re.split("(\<.+?\>)", query) + re.split('(".+?")', query)
            if u.startswith(
                (f"<http://dbpedia.org/{field}", f"<https://dbpedia.org/{field}")
            )
        ]
    for field in urls_quotient.keys():
        for url in urls_quotient[field]:
            _url = url.split("/")[-1]
            _lev = {_term: levenshtein(_term, _url) for _term in mapping.keys()}
            term = min(_lev, key=_lev.get)
            mapping_replace[url] = f"db{field[0]}_{mapping[term]}"
    query = do_replacements(query, mapping_replace)
    return query, mapping_replace


def simplify_english_request(eng_query):
    return eng(eng_query, blind_create_mapping(eng_query))


def simplify_database(DATASET_PATH, json_db, OUT_FILE):
    possible_english_labels = ["intermediary_question"]
    for label in possible_english_labels:
        if label in json_db[0].keys():
            english_label = label
            break
    if "sparql_query" in json_db[0].keys():
        sparql_bool = True
    if "datalog_query" in json_db[0].keys():
        datalog_query = True

    converted_queries = []
    for s in json_db:
        # domain specific mapping:
        # mapping = create_mapping(s['sparql_query'])
        # blind mapping:
        mapping = blind_create_mapping(s[english_label])
        eng_query, _ = eng(s[english_label], mapping)
        converted_query = {"_id": s["_id"], english_label: eng_query}
        if sparql_bool:
            # sparql_query = (sparql(s['sparql_query'], mapping))
            sparql_query, _ = blind_sparql(s["sparql_query"], mapping)
            converted_query["sparql_query"] = sparql_query

        if datalog_query:
            # datalog_query = (datalog(s['datalog_query'], mapping))
            datalog_query, _ = blind_datalog(s["datalog_query"], mapping)
            converted_query["datalog_query"] = datalog_query
        converted_queries.append(converted_query)

    with open(f"{DATASET_PATH}/{OUT_FILE}", "w") as out:
        out.write(json.dumps(converted_queries))


if __name__ == "__main__":
    DATASET_PATH = "../datasets/LC-QuAD/"
    DATASET_NAME = "LC-QuAD"
    DATASET_FILE = "train-data-datalog.json"
    OUT_FILE = "KB_simplified_train-data-datalog.json"
    # Data sources
    N = 1000000
    json_db = json.load(open(DATASET_PATH + DATASET_FILE))
    json_db = json_db[: min(len(json_db), N)]
    # some queries arent correctly processed by darling, remove them
    json_db = [s for s in json_db if s["datalog_query"] != "."]

    simplify_database(DATASET_PATH, json_db, OUT_FILE)
