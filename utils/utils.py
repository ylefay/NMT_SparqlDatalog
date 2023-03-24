import re
from typing import Dict

def levenshtein(mot1, mot2):
    ligne_i = [k for k in range(len(mot1) + 1)]
    for i in range(1, len(mot2) + 1):
        ligne_prec = ligne_i
        ligne_i = [i] * (len(mot1) + 1)
        for k in range(1, len(ligne_i)):
            cout = int(mot1[k - 1] != mot2[i - 1])
            ligne_i[k] = min(
                ligne_i[k - 1] + 1, ligne_prec[k] + 1, ligne_prec[k - 1] + cout
            )
    return ligne_i[len(mot1)]


def do_replacements(string, rep_dict:Dict[str, str]):
    if rep_dict:
        pattern = re.compile(
            "|".join([re.escape(k) for k in sorted(rep_dict, key=len, reverse=True)]),
            flags=re.DOTALL,
        )
        return pattern.sub(lambda x: rep_dict[x.group(0)], string)
    return string


def do_replacements_except(string, mapping_replace:Dict[str, str], split:str, exceptions:Dict[str, str]):
    words = string.split(split)
    for idx, word in enumerate(words):
        if not sum([exception in word for exception in exceptions]):
            words[idx] = do_replacements(word, mapping_replace)
    return split.join(words)


def datalog_preprocessing(query):
    mapping_replace = {
        "<": " br_open ",
        ">": " br_close ",
        '"': " quote ",
        "https://dbpedia.org/resource/": "dbr_",
        "https://dbpedia.org/ontology/": "dbo_",
        "https://dbpedia.org/property/": "dbp_",
        "http://purl.org/dc/terms/subject": "dct_subject",
        "http://www.w3.org/2003/01/geo/wgs84_pos#lat": "geo_lat",
        "http://www.georss.org/georss/point": "georss_point",
        "http://www.w3.org/2003/01/geo/wgs84_pos#long": "geo_long",
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf_type",
        "http://dbpedia.org/resource/": "dbr_",
        "http://dbpedia.org/ontology/": "dbo_",
        "http://dbpedia.org/property/": "dbp_",
    }
    query = do_replacements(query, mapping_replace)
    mapping_replace = {
        ".": " dot ",
        ",": " float ",
        "(": " par_open ",
        ")": " par_close ",
    }
    exceptions = query.split(" ")
    exceptions = [
        word
        for word in exceptions
        if word.startswith(
            ("dbo_", "dbr_", "dbp_")
            or word in ["geo_lat", "georss_point", "geo_long", "rdf_type"]
        )
    ]
    query = do_replacements_except(query, mapping_replace, " ", exceptions)
    query = " ".join(query.split())
    return query


def datalog_invert_preprocessing(query):
    mapping_replace = {"dot": ".", "float": ","}
    query = do_replacements(query, mapping_replace)
    mapping_replace = {
        "<": "br_open",
        ">": "br_close",
        "(": "par_open",
        ")": "par_close",
        '"': "quote",
        "https://dbpedia.org/resource/": "dbr_",
        "https://dbpedia.org/ontology/": "dbo_",
        "http://dbpedia.org/property/": "dbp_",
        "http://purl.org/dc/terms/subject": "dct_subject",
        "http://www.w3.org/2003/01/geo/wgs84_pos#lat": "geo_lat",
        "http://www.georss.org/georss/point": "georss_point",
        "http://www.w3.org/2003/01/geo/wgs84_pos#long": "geo_long",
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf_type",
    }
    mapping_replace = {mapping_replace[key]: key for key in mapping_replace.keys()}
    query = do_replacements(query, mapping_replace)
    query = query.replace(" ", "")
    query = query.replace(":-", " :- ")
    return query


def sparql_preprocessing(query):
    mapping_replace = {
        "{": " br_open ",
        "}": " br_close ",
        "<": " cr_open ",
        ">": " cr_close ",
        '"': " quote ",
        "https://dbpedia.org/resource/": "dbr_",
        "https://dbpedia.org/ontology/": "dbo_",
        "https://dbpedia.org/property/": "dbp_",
        "http://purl.org/dc/terms/subject": "dct_subject",
        "http://www.w3.org/2003/01/geo/wgs84_pos#lat": "geo_lat",
        "http://www.georss.org/georss/point": "georss_point",
        "http://www.w3.org/2003/01/geo/wgs84_pos#long": "geo_long",
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf_type",
        "http://dbpedia.org/resource/": "dbr_",
        "http://dbpedia.org/ontology/": "dbo_",
        "http://dbpedia.org/property/": "dbp_",
        "?": "var_",
    }
    query = do_replacements(query, mapping_replace)
    mapping_replace = {
        ".": " dot ",
        ",": " float ",
        "(": " par_open ",
        ")": " par_close ",
    }
    exceptions = query.split(" ")
    exceptions = [
        word
        for word in exceptions
        if word.startswith(
            ("dbo_", "dbr_", "dbp_")
            or word in ["geo_lat", "georss_point", "geo_long", "rdf_type"]
        )
    ]
    query = do_replacements_except(query, mapping_replace, " ", exceptions)
    query = " ".join(query.split())
    return query


def sparql_invert_preprocessing(query):
    mapping_replace = {" dot ": " . ", " float ": ","}
    query = do_replacements(query, mapping_replace)
    mapping_replace = {
        "{": "br_open",
        "}": "br_close",
        "<": "cr_open",
        ">": "cr_close",
        "(": "par_open",
        ")": "par_close",
        '"': "quote",
        "https://dbpedia.org/resource/": "dbr_",
        "https://dbpedia.org/ontology/": "dbo_",
        "http://dbpedia.org/property/": "dbp_",
        "http://purl.org/dc/terms/subject": "dct_subject",
        "http://www.w3.org/2003/01/geo/wgs84_pos#lat": "geo_lat",
        "http://www.georss.org/georss/point": "georss_point",
        "http://www.w3.org/2003/01/geo/wgs84_pos#long": "geo_long",
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf_type",
        "?": "var_",
    }
    mapping_replace = {mapping_replace[key]: key for key in mapping_replace.keys()}
    query = do_replacements(query, mapping_replace)
    query = do_replacements(query, {"< ": "<", " >": ">"})
    query = re.sub(" +", " ", query)
    return query


def drop_brackets(query: str):
    return query.replace("<", "").replace(">", "")

