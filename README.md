# NMT
An NMT pipeline between english and Sparql/Datalog queries.

A fork from https://github.com/LiberAI/NSpM that aims to mitigate the issue that comes from the absence, in the training database, of terms specific to the ontology, resources or the properties we are learning on. Those terms are called Knowledge-Base specific terms.

The NMT model is based on the Seq2Seq implementation by Google AI Research team.

The main ideas behind the pipeline are the following:
* Convert SPARQL databases into Datalog databases using DaRLing.
* Exploit already tagged questions (intermediary_question field on the LC-QuAD database) as well as BERT POS tags to automatically detect Knowledge-Base specific terms (using a Seq2Seq model) and simplify them by replacing those terms with variables.
* Learn (using a Seq2Seq model) how to predict the simplified queries from the simplified questions.

Then given a question:
* Simplify it by using the (POS tags, KB tags) model. 
* Use the (Simplified English questions, Sparql/Datalog simplified queries) model to predict the simplified query.
* Replace back the simplified terms.

# Codes and their usages
## /darling/: Using DaRLing a SPARQL-Datalog query rewriter, with multiprocessing to process large SPARQL datasets.
This script is independant from the rest of the project. 
Use `darling.py` to simultaneously run multiple darling instances to convert large SPARLQ datasets. After having edited the head of `darling.py` to ensure the loading of your json dataset, run:
```
python darling.py
```

Head example:
```
DATASET_PATH = "../datasets/LC-QuAD/"
DATASET_NAME = "LC-QuAD"
DATASET_FILE = "train-data.json"
ontology_name = 'ontology--DEV_type=parsed.ttl' #expected location : ./inputs/{ontology_name}
json_db = json.load(open(DATASET_PATH+DATASET_FILE))
sparql_txt = [s['sparql_query'] for s in json_db]
OUT_FILE = "train-data-datalog.json"
```

Such heads are present everywhere in the project, please be aware you must change them corresponding to your needs.

The script creates a file located in `../datasets/LC-QuAD/train-data-datalog.json` with an additional field `datalog_query`.

For example:
```
{
        "_id": "2972",
        "corrected_question": "List all the mmebers of  Mekong River Commission?",
        "intermediary_question": "What are the <membership> of <Mekong River Commissio> ?",
        "sparql_query": " SELECT DISTINCT ?uri WHERE { <http://dbpedia.org/resource/Mekong_River_Commission> <http://dbpedia.org/property/membership> ?uri } ",
        "sparql_template_id": 2,
        "datalog_query": "ans(uri) :- <http://dbpedia.org/property/membership>(\"http://dbpedia.org/resource/Mekong_River_Commission\",uri)."
}
```
## /datasets/: Contains LC-QuAD database, a template generated Monument DBPedian database and a script with CSV templates to generate SPARQL datasets.
This part is independant from the rest of the project. In `./templates/`, use `generator.py` to generate data.{en, datalog} files using CSV templates.

You can use those generated SPARQL queries to create a datalog dataset. In order to do that, you first have to create a json file with darling-compatible syntax. Use `../utils/json_constructor.py` to do so.

For example, running:
```
python generator.py --templates ./annotations_monument.csv --output ../monument_600
cd ../utils
python json_constructor.py
```

will creates in the folder `../monument_600`, the following files: `data.en`, `data.sparql`, `monument_600.json`. The two data files are to be fed to `../../generate.sh` if one wants to run the NMT script on the SPARQL side. Otherwise, you want to feed back `monument_600.json` to darling.

## /nmt/: the Seq2seq implementation
Usage:

```
python -m nmt.nmt --src=$SRC_EXTENSION --tgt=$TGT_EXTENSION --vocab_prefix=../$DATASET/vocab --dev_prefix=../$DATASET/dev --test_prefix=../$DATASET/test --train_prefix=../$DATASET/train --out_dir=../$MODEL --num_train_steps=$NUM_TRAIN_STEPS --steps_per_stats=100 --num_layers=2 --num_units=128 --dropout=0.2 --metrics=bleu
 
python -m nmt.nmt  --vocab_prefix=../$MODEL/vocab --model_dir=../$MODEL  --inference_input_file=./to_ask.txt  --inference_output_file=./output.txt --out_dir=../$MODEL --src=$SRC_EXTENSION --tgt=$TGT_EXTENSION | tail -n4

 ```

This part is used by `../train.sh` and `../ask.sh`.

## /utils/pos.py: From an existing database with tagged knowledge-base specific terms in the english queries, this script creates a mapping between grammar classes (BERT POS tags) and KB-specific tags.
The purpose of this part is to then use the Seq2Seq model to learn how to detect KB specific terms in order to simplify them.

`./pos.py` creates `../datasets/LC-QuAD_bert_tag.json` file that contains the mapping between BERT POS tags and KB tags. 

For example, given the following KB-tagged english question:
    
    "What is the <alumnus of> of the <fashion designer> whose <death place> is <Stony Brook University Hospital> ?"

That has the following BERT POS tags:

    WP VBZ DT NN IN IN DT NN NN WP$ NN NN VBZ NNP NNP NNP NNP .

The function `br_tagging` enables us to create the following tags:
    
    N N N O E N N O E N O E N O I I E N

With both a total of 18 tags. The KB tags are the following ones:

| Abbreviated tag | Tag  |         Corresponds to a token          |
|:----------------:|:-----:|:---------------------------------------:|
|        N         |  No   |         that is not KB-specific         |
|        O         | Open  |   that starts a KB-specific sequence    |
|        E         |  End  |      that ends a KB-specific seq.       |
|        B         | Both  | that starts and ends a KB-specific seq. |
|        I         | Inner |    that is inside a KB-specific seq.    |

The extension of the files containing KB tags is ".br" for brackets.


## /utils/: Contains important utilitaries functions, with datalog and sparql preprocessing/tokenization and inverse preprocessing functions as well as the KB simplification script.



Running `python ./KB_simplification.py` creates `../datasets/LC-QuAD/KB_simplified_train-data-datalog.json` that contains KB simplified requests.

For example 
```
{
        "_id": "54",
        "corrected_question": "Name the island with archipelago as Society Islands and has the largest city named Faaa ?",
        "intermediary_question": "What is the <island> whose <largest city> is <Faaa> and <archipelago> is <Society Islands>?",
        "sparql_query": "SELECT DISTINCT ?uri WHERE {?uri <http://dbpedia.org/ontology/largestCity> <http://dbpedia.org/resource/Faaa> . ?uri <http://dbpedia.org/property/archipelago> <http://dbpedia.org/resource/Society_Islands>  . ?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/Island>}",
        "sparql_template_id": 308,
        "datalog_query": "ans(uri) :- <http://dbpedia.org/ontology/Island>(uri),<http://dbpedia.org/property/archipelago>(uri,\"http://dbpedia.org/resource/Society_Islands\"),<http://dbpedia.org/ontology/largestCity>(uri,\"http://dbpedia.org/resource/Faaa\")."
}
```
is mapped to
```
{
        "_id": "54",
        "intermediary_question": "What is the <A> whose <B> is <C> and <D> is <E>?",
        "sparql_query": "SELECT DISTINCT ?uri WHERE {?uri <dbo_B> <dbr_C> . ?uri <dbp_D> <dbr_E>  . ?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <dbo_A>}",
        "datalog_query": "ans(uri) :- <dbo_A>(uri),<dbp_D>(uri,\"dbr_E\"),<dbo_B>(uri,\"dbr_C\")."
}
```
The simplification is done by replacing each term in brackets in the intermediary question with variables, replacing their occurences in the sparql and datalog query with the corresponding variable, using Levenshtein distance.

The NMT model will learn on the KB simplified requests. That is why we need to learn how to detect the KB simplified terms (see the previous section) so that we are able to simplify the input question.

Running `python data_constructor.py` creates from the json files, the needed data files (for the three models, (BERT, KB), (en, sparql), (en, datalog)).

## Main folder: 
`./generate.sh` to create from the data files the vocabulary files as well as the train, test and dev sets. 

Usage:
```
./generate.sh $DATASET $SRC_EXT $TGT_EXT
```
Example usage:
```
./generate.sh ./datasets/LC-QuAD en sparql
```

Where (SRC_EXT, TGT_EXT) = (bert, br) for (BERT tags, KB tags) model, (en, sparql) or (en, datalog)

`./train.sh` to train a NMT model.

Usage:
```
./train.sh $DATASET $MODEL $NUM_TRANING_STEPS $SRC_EXT $TGT_EXT
```
Example usage:
```
./train.sh ./datasets/LC-QuAD ./trained_models/LC-QuAD_bert_br 12000 bert br
```

`./ask.sh` to perform a prediction using an existing trained model. There is a postprocessing function to invert the tokenization process.

Usage:
```
./ask.sh $MODEL $QUESTION $SRC_EXT $TGT_EXT
```
Example usage:
```
./ask.sh ./trained_models/LC-QuAD_bert_br "WP VBZ DT NN WP$ JJS NN VBZ NNP CC NN VBZ NNP NNPS ." bert br
```

Caution:

Running consecutively `./generate.sh` for the pairs (en, datalog) and (en, sparql) creates a conflict with `$DATASET/data.en`. You must perform consecutively `./generate.sh` and `./train.sh` on (en, datalog) then on (en, sparql).