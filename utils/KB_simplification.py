from utils import levenshtein, do_replacements
import json
import re


# Create a mapping between kb specific terms in the English query and generic symbols, A, B, ...
# do not specify to which domain the kb specific term belongs
def blind_create_mapping(query):
    kb_specific_terms = [
        u[1:-1] for u in re.split("(\<.+?\>)", query) if len(u) > 0 and u[0] == "<"
    ]
    mapping = {}
    for term in kb_specific_terms:
        if term not in mapping.keys():
            mapping[term] = f"{chr(65+len(mapping.keys()))}"
    return mapping

# Create a mapping between kb specific terms in the English query and generic symbols, A, B, ...
# Such that the predecessor of the generic symbol by the mapping is the closest to the kb term
# using the levenshtein distance.
def eng(query, mapping):
    terms = [u[1:-1] for u in re.split("(\<.+?\>)", query) if u.startswith("<")]
    mapping_replace = {}
    for term in terms:
        _lev = {_obj: levenshtein(term, _obj) for _obj in mapping.keys()}
        obj = min(_lev, key=_lev.get)
        mapping_replace[term] = mapping[obj]
    query = do_replacements(query, mapping_replace)
    return query, mapping_replace

# Same as the previous function but given a SPARQL query. We keep the 'field' information 
# For example, if the KB term is dbpedia.org/resource/Jesus_Christ and the mapping gives
# 'A' for 'Jesus Christ', then the returned mapping will contains 'dbpedia.org/resource/Jesus_Christ':'dbr_A'.
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

# Same as the previous function for Datalog queries.
def blind_datalog(query, mapping):
    urls_quotient = {"ontology": [], "resource": [], "property": []}
    mapping_replace = {}
    for field in urls_quotient.keys():
        urls_quotient[field] = [
            u[1:-1]
            for u in re.split("(\<.+?\>)", query)
            if u.startswith(
                (f"<http://dbpedia.org/{field}", f"<https://dbpedia.org/{field}")
            )
        ]
        urls_quotient[field] = urls_quotient[field] + [
            u[1:-1]
            for u in re.split('(".+?")', query)
            if u.startswith(f'"http://dbpedia.org/{field}')
            or u.startswith(f'"https://dbpedia.org/{field}')
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


def simplify_database(json_db, OUTFILE_PATH):
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
        mapping = blind_create_mapping(s[english_label])
        eng_query, _ = eng(s[english_label], mapping)
        converted_query = {"_id": s["_id"], english_label: eng_query}
        if sparql_bool:
            sparql_query, _ = blind_sparql(s["sparql_query"], mapping)
            converted_query["sparql_query"] = sparql_query

        if datalog_query:
            datalog_query, _ = blind_datalog(s["datalog_query"], mapping)
            converted_query["datalog_query"] = datalog_query
        converted_queries.append(converted_query)

    with open(OUTFILE_PATH, "w") as out:
        out.write(json.dumps(converted_queries))


if __name__ == "__main__":
    DATASET_PATH = "../datasets/LC-QuAD/"
    DATASET_NAME = "LC-QuAD"
    DATASET_FILE = "data-datalog.json"
    OUTFILE_PATH = DATASET_PATH+"/KB_simplified_data-datalog.json"
    # Data sources
    N = 1000000
    json_db = json.load(open(DATASET_PATH + DATASET_FILE))
    json_db = json_db[: min(len(json_db), N)]
    # some queries arent correctly processed by darling, remove them
    json_db = [s for s in json_db if s["datalog_query"] != "."]

    simplify_database(json_db, OUTFILE_PATH)
