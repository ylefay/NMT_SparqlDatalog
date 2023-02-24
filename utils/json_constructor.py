import json
from ..datasets.templates.generator_utils import reverse_shorten_query, reverse_replacements
from .utils import do_replacements

# Construct the darling-adapted json file.


# Process the query so that it is darling compatible
def preprocessing(query):
    mapping_replace = {'dbo_': '<https://dbpedia.org/ontology/', 'dbr_': '<https://dbpedia.org/resource/',
                       'dbp_': '<http://dbpedia.org/property/', 'dct_subject': '<http://purl.org/dc/terms/subject>',
                       'geo_lat': '<http://www.w3.org/2003/01/geo/wgs84_pos#lat>',
                       'georss_point': '<http://www.georss.org/georss/point>',
                       'geo_long': '<http://www.w3.org/2003/01/geo/wgs84_pos#long>',
                       'rdf_type': '<http://www.w3.org/1999/02/22-rdf-syntax-ns#>'}
    query = do_replacements(query, mapping_replace)
    startswith_add_to_the_end = ('<https://dbpedia.org/ontology/',
                                 '<https://dbpedia.org/resource/', '<http://dbpedia.org/property/')
    mapping_replace = {w: w[:-1] for w in query.split(' ') if w.startswith(
        startswith_add_to_the_end) and ')' == w[-1] and '(' not in w}
    # query = do_replacements(query, mapping_replace)
    mapping_replace = {w: w+'>' for w in query.split(' ') if w.startswith(
        startswith_add_to_the_end) and w[-1] != ')' and w[-1] != "_"}
    mapping_replace.update({w: w[:-1]+'>)' for w in query.split(' ')
                           if w.startswith(startswith_add_to_the_end) and w[-1] == ')'})
    print(mapping_replace)
    # print([w for w in query.split(' ') if w.startswith(startswith_add_to_the_end)])
    query = do_replacements(query, mapping_replace)
    query = reverse_shorten_query(query)
    query = reverse_replacements(query)
    mapping_replace = {word: word[:-1] for word in query.split(' ') if word.startswith(
        startswith_add_to_the_end) and ',_' in word and ')' in word}
    query = do_replacements(query, mapping_replace)
    mapping_replace = {
        ')}order': ')} order', 'orde by': 'order by', 'where{<': 'where { <', "{{": '{ {', ' ) ': ')>', ' where{ ': ' where { '}
    query = do_replacements(query, mapping_replace)
    return query

# Create the json file.


def convert_database(DATASET_PATH, DATASET_FILE, file_paths):

    lines = [open(DATASET_PATH+file_path).readlines()
             for file_path in file_paths]

    json_db = [
        {
            '_id': idx,
            'question': lines[0][idx][:-1],
            'sparql_query':preprocessing(lines[1][idx][:-1])
        }
        # some filtering
        for idx in range(len(lines[0])) if lines[1][idx][:3] != "ask"
    ]
    json_db = [
        x for x in json_db if "FILTER(" not in x['sparql_query'] and 'UNION{' not in x['sparql_query'] and ' <B>' not in x['sparql_query']
    ]  # some filtering

    with open(DATASET_PATH + DATASET_FILE, 'w') as outfile:
        outfile.write(json.dumps(json_db))
    outfile.close()


if __name__ == '__main__':
    example_query = 'select wildcard where brack_open brack_open dbr_Diana_the_Huntress_Fountain var_a var_b sep_dot dbr_Pausanias_ attr_open geographer attr_close var_a var_b brack_close UNION brack_open brack_open dbr_Diana_the_Huntress_Fountain var_a var_b sep_dot dbr_Pausanias_(geographer) var_a var_b brack_close UNION brack_open var_c var_d dbr_Diana_the_Huntress_Fountain sep_dot var_c var_d dbr_Pausanias_(geographer) brack_close brack_close UNION brack_open var_c var_d dbr_Diana_the_Huntress_Fountain sep_dot var_c var_d dbr_Pausanias_ attr_open geographer attr_close brack_close brack_close'
    
    DATASET_PATH = "../datasets/monument_600/"
    DATASET_NAME = "monument_600"
    DATASET_FILE = "monument_600.json"
    file_paths = [
        'data.en',
        'data.sparql'
    ]
    convert_database(DATASET_PATH, DATASET_FILE, file_paths)
