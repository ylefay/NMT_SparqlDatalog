def levenshtein(mot1, mot2):
    ligne_i = [k for k in range(len(mot1)+1)]
    for i in range(1, len(mot2) + 1):
        ligne_prec = ligne_i
        ligne_i = [i]*(len(mot1)+1)
        for k in range(1, len(ligne_i)):
            cout = int(mot1[k-1] != mot2[i-1])
            ligne_i[k] = min(ligne_i[k-1] + 1, ligne_prec[k] +
                             1, ligne_prec[k-1] + cout)
    return ligne_i[len(mot1)]


def forget_tokens(tokens, forget_list):
    return [token for token in tokens if token not in forget_list]


def do_replacements(string, mapping_replace):
    for to_replace in sorted(mapping_replace, key=len, reverse=True):
        string = string.replace(to_replace, mapping_replace[to_replace])
    return string


def do_replacements_except(string, mapping_replace, split, exceptions):
    words = string.split(split)
    for idx, word in enumerate(words):
        if word not in exceptions:
            words[idx] = do_replacements(word, mapping_replace)
    return split.join(words)


def datalog_preprocessing(query):
    mapping_replace = {'<': ' br_open ', '>': ' br_close ',
                       '"': ' quote ', 'https://dbpedia.org/resource/': 'dbr_', 'https://dbpedia.org/ontology/': 'dbo_', 'https://dbpedia.org/property/': 'dbp_',
                       'http://purl.org/dc/terms/subject': 'dct_subject',
                       'http://www.w3.org/2003/01/geo/wgs84_pos#lat': 'geo_lat',
                       'http://www.georss.org/georss/point': 'georss_point',
                       'http://www.w3.org/2003/01/geo/wgs84_pos#long': 'geo_long',
                       'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf_type',
                       'http://dbpedia.org/resource/': 'dbr_', 'http://dbpedia.org/ontology/': 'dbo_', 'http://dbpedia.org/property/': 'dbp_',
                       }
    query = do_replacements(query, mapping_replace)
    mapping_replace = {'.': ' dot ',  ',': ' float ',
                       '(': ' par_open ', ')': ' par_close ', }
    exceptions = query.split(' ')
    exceptions = [word for word in exceptions if word.startswith(
        ('dbo_', 'dbr_', 'dbp_') or word in ['geo_lat', 'georss_point', 'geo_long', 'rdf_type'])]
    query = do_replacements_except(query, mapping_replace, ' ', exceptions)
    query = ' '.join(query.split())
    return query


def datalog_invert_preprocessing(query):
    mapping_replace = {' dot ': '.', ' float ': ','}
    query = do_replacements(query, mapping_replace)
    mapping_replace = {'<': ' br_open ', '>': ' br_close ', '(': ' par_open ', ')': ' par_close ',
                       '"': ' quote ', 'https://dbpedia.org/resource/': 'dbr_', 'https://dbpedia.org/ontology/': 'dbo_', 'http://dbpedia.org/property/': 'dbp_',
                       'http://purl.org/dc/terms/subject': 'dct_subject',
                       'http://www.w3.org/2003/01/geo/wgs84_pos#lat': 'geo_lat',
                       'http://www.georss.org/georss/point': 'georss_point',
                       'http://www.w3.org/2003/01/geo/wgs84_pos#long': 'geo_long',
                       'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf_type'}
    mapping_replace = {mapping_replace[key]                       : key for key in mapping_replace.keys()}
    query = do_replacements(query, mapping_replace)
    # since we remove successive spaces, we need to replace par_open, dot etc
    mapping_replace = {'par_open': '(', 'par_close': ')', 'quote': '"',
                       ')dot': ').', 'br_close': '>', 'br_open': '<', 'float': ','}
    query = do_replacements(query, mapping_replace)
    query = query.replace(' ', '')
    query = query.replace(':-', ' :- ')
    return query


def sparql_preprocessing(query):
    mapping_replace = {'{': ' br_open ', '}': ' br_close ', '<': ' cr_open ', '>': ' cr_close ',
                       '"': ' quote ', 'https://dbpedia.org/resource/': 'dbr_', 'https://dbpedia.org/ontology/': 'dbo_', 'https://dbpedia.org/property/': 'dbp_',
                       'http://purl.org/dc/terms/subject': 'dct_subject',
                       'http://www.w3.org/2003/01/geo/wgs84_pos#lat': 'geo_lat',
                       'http://www.georss.org/georss/point': 'georss_point',
                       'http://www.w3.org/2003/01/geo/wgs84_pos#long': 'geo_long',
                       'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf_type',
                       'http://dbpedia.org/resource/': 'dbr_', 'http://dbpedia.org/ontology/': 'dbo_', 'http://dbpedia.org/property/': 'dbp_',
                       '?': 'var_'}
    query = do_replacements(query, mapping_replace)
    mapping_replace = {'.': ' dot ',  ',': ' float ',
                       '(': ' par_open ', ')': ' par_close ', }
    exceptions = query.split(' ')
    exceptions = [word for word in exceptions if word.startswith(
        ('dbo_', 'dbr_', 'dbp_') or word in ['geo_lat', 'georss_point', 'geo_long', 'rdf_type'])]
    query = do_replacements_except(query, mapping_replace, ' ', exceptions)
    query = ' '.join(query.split())
    return query


def sparql_invert_preprocessing(query):
    mapping_replace = {' dot ': '.', ' float ': ','}
    query = do_replacements(query, mapping_replace)
    mapping_replace = {'{': ' br_open ', '}': ' br_close ',  '<': ' cr_open ', '>': ' cr_close ', '(': ' par_open ', ')': ' par_close ',
                       '"': ' quote ', 'https://dbpedia.org/resource/': 'dbr_', 'https://dbpedia.org/ontology/': 'dbo_', 'http://dbpedia.org/property/': 'dbp_',
                       'http://purl.org/dc/terms/subject': 'dct_subject',
                       'http://www.w3.org/2003/01/geo/wgs84_pos#lat': 'geo_lat',
                       'http://www.georss.org/georss/point': 'georss_point',
                       'http://www.w3.org/2003/01/geo/wgs84_pos#long': 'geo_long',
                       'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf_type',
                       '?': 'var_'}
    mapping_replace = {mapping_replace[key]                       : key for key in mapping_replace.keys()}
    query = do_replacements(query, mapping_replace)
    # since we remove successive spaces, we need to replace par_open, dot etc
    mapping_replace = {'par_open': '(', 'par_close': ')', ' quote': '"',
                       ')dot': ').', ' br_close': '}', 'cr_close': '>', 'cr_open': '<'}
    query = do_replacements(query, mapping_replace)
    return query
