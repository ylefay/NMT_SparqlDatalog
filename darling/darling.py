import json 
import os
from multiprocessing import Process

N_cpu = 8

# Data sources

#for the monument dataset:
DATASET_PATH = "../datasets/monument_600/"
DATASET_NAME = "monument_600"
DATASET_FILE = "monument_600.json"
ontology_name = 'Monument_ontology.ttl' #expected location: ./inputs/{ontology_name}
json_db = json.load(open(DATASET_PATH+DATASET_FILE))
sparql_txt = [s['sparql_query'] for s in json_db]

#for the LC-QuAD dataset:
#DATASET_PATH = "../datasets/LC-QuAD/"
#DATASET_NAME = "LC-QuAD"
#DATASET_FILE = "train-data.json"
#ontology_name = 'ontology--DEV_type=parsed.ttl' #expected location : ./inputs/{ontology_name}
#json_db = json.load(open(DATASET_PATH+DATASET_FILE))
#sparql_txt = [s['sparql_query'] for s in json_db]

OUT_FILE = "train-data-datalog.json"

force_idx = None #force run darling_run over force_idx

def darling_run(sparql_queries_iter_index, ontology_name):
    for idx in sparql_queries_iter_index:
        if not os.path.exists(f'./outputs/query_{idx}.asp') or force_idx and idx in force_idx or os.path.getsize(f'./outputs/query_{idx}.asp') == 0:
            s = sparql_txt[idx]
            print(f'{idx}:{s}')

            #preprocess the queries, darling does not work with select distinct count(?uri) ..
            #write the query in /inputs/queries_{idx}.sparql to be fed to darling
            with open(f"./inputs/queries_{idx}.sparql", "w") as file:
                if "SELECT DISTINCT COUNT(?uri) WHERE" in s:
                    s = s.replace("SELECT DISTINCT COUNT(?uri) WHERE", "SELECT (COUNT(distinct ?uri) as ?count) WHERE")
                    s+=" GROUP BY ?uri"
                if s[0] == " ":
                    s = s[1:]
                file.write(s+"\n")

            #managing inputs and outputs 
            os.system(f'cp ./inputs/{ontology_name} ./inputs/{ontology_name[:-4]}_{idx}.ttl')
            os.system(f'perl darling.pl -q ./inputs/queries_{idx}.sparql -t ./inputs/{ontology_name[:-4]}_{idx}.ttl')
            os.system(f'mv ./{ontology_name[:-4]}_{idx}_query_1.asp ./outputs/_query_{idx}.asp')
            os.system(f'rm ./inputs/{ontology_name[:-4]}_{idx}.ttl')

            #Keep one converted ontology
            if os.path.exists(f'./{ontology_name[:-4]}.asp'): 
                os.system(f'rm ./{ontology_name[:-4]}_{idx}.asp')
            else:
                os.system(f'mv ./{ontology_name[:-4]}_{idx}.asp ./{ontology_name[:-4]}.asp')

            #keep only the translated query and delete the translated ontology
            os.system(f'head -n 1 ./outputs/_query_{idx}.asp > ./outputs/query_{idx}.asp')
            os.system(f'rm ./outputs/_query_{idx}.asp')
            os.system(f'rm ./inputs/queries_{idx}.sparql')


if __name__ == '__main__':
    #execute darling using multiprocessing
    processes = [Process(target=darling_run, args=([k+N_cpu*i for i in range(len(sparql_txt)//N_cpu)],ontology_name,)) for k in range(N_cpu)]
    if not force_idx:
        for p in processes:
            p.start()
    if force_idx:
        darling_run(force_idx)
    while sum([p.is_alive() for p in processes]):
        True

    #adding to the json the corresponding datalog queries
    for idx, s in enumerate(json_db):
        with open(f'./outputs/query_{idx}.asp') as query_file:
            s['datalog_query'] = query_file.read()[:-1]
            json_db[idx] = s

    #export the constructed json
    with open(DATASET_PATH + OUT_FILE, "w") as outfile:
        outfile.write(json.dumps(json_db))  
