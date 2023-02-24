import json 
import os
from multiprocessing import Process

N_cpu = 8

DATASET_PATH = "../pytorch-seq2seq/SPARQL_NL/dataset/LC-QuAD/"
DATASET_NAME = "LC-QuAD"

SPARQL_QUERIES_PATH = "./inputs/queries.sparql"

# Data sources
#english_txt = open(DATASET_PATH + "temp.en", encoding="utf8").read().split("\n")
#sparql_txt = open(DATASET_PATH + "temp.sparql", encoding="utf8").read().split("\n")
json_db = json.load(open(DATASET_PATH+"train-data.json"))
english_txt = [s['corrected_question'] for s in json_db]
sparql_txt = [s['sparql_query'] for s in json_db]

force_idx = None

def darling_run(sparql_queries_iter_index):
    for idx in sparql_queries_iter_index:
        if not os.path.exists(f'./outputs/query_{idx}.asp') or force_idx and idx in force_idx:
            s = sparql_txt[idx]
            print(f'{idx}:{s}')
            with open(f"./inputs/queries_{idx}.sparql", "w") as file:
                if "SELECT DISTINCT COUNT(?uri) WHERE" in s:
                    s = s.replace("SELECT DISTINCT COUNT(?uri) WHERE", "SELECT (COUNT(distinct ?uri) as ?count) WHERE")
                    s+=" GROUP BY ?uri"
                if s[0] == " ":
                    s = s[1:]
                file.write(s+"\n")
            file.close()
            os.system(f'cp ./inputs/ontology--DEV_type\=parsed.ttl ./inputs/ontology--DEV_type\=parsed_{idx}.ttl')
            os.system(f'perl darling.pl -q ./inputs/queries_{idx}.sparql -t ./inputs/ontology--DEV_type\=parsed_{idx}.ttl')
            os.system(f'mv ./ontology--DEV_type=parsed_{idx}_query_1.asp ./outputs/_query_{idx}.asp')
            os.system(f'rm ./inputs/ontology--DEV_type\=parsed_{idx}.ttl')
            if idx!= 0: 
                os.system(f'rm ./ontology--DEV_type\=parsed_{idx}.asp')
            os.system(f'head -n 1 ./outputs/_query_{idx}.asp > ./outputs/query_{idx}.asp')
            os.system(f'rm ./outputs/_query_{idx}.asp')
            os.system(f'rm ./inputs/queries_{idx}.sparql')

if __name__ == '__main__':
    #execute darling using multiprocessing
    processes = [Process(target=darling_run, args=([k+N_cpu*i for i in range(len(sparql_txt)//N_cpu)],)) for k in range(N_cpu)]
    if not force_idx:
        for p in processes:
            p.start()
    if force_idx:
        darling_run(force_idx)
    while sum([p.is_alive() for p in processes]):
        True
    #adding to the json the corresponding datalog queries
    for idx, s in enumerate(json_db):
        with open(f'./outputs/query_{idx}.asp') as file:
            s['datalog_query'] = file.read()[:-1]
            json_db[idx] = s
    #writing it    
    with open(DATASET_PATH + "train-data-datalog.json", "w") as outfile:
        outfile.write(json.dumps(json_db))  