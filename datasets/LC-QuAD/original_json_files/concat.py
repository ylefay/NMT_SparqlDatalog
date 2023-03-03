import json

files_to_concat = ['./train-data.json', './test-data.json']

json_db = []

for file in files_to_concat:
    json_db += (json.load(open(file)))


with open('./data.json', 'w+') as out:
    out.write(json.dumps(json_db))
