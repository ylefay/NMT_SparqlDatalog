import os
from POS_BR_tags.pos import br_tagging, pipeline, fix_pipeline
from utils.utils import do_replacements, do_replacements_except
from utils.KB_simplification import simplify_english_request
import tempfile


def full_pipeline(ce_untagged_query,  src_tgt_MODEL_PATH, src, tgt, exceptions_for_replace, silent, bert_br_MODEL_PATH="./trained_models/LC-QuAD_bert_br"):
    temp_file = tempfile.NamedTemporaryFile().name
    if not silent:
        print(f"Query: {ce_untagged_query}")

    # Tagging KB specific terms
    piped_query = fix_pipeline(pipeline(ce_untagged_query))
    bert_pos_tags = " ".join([el["entity"] for el in piped_query])
    if not silent:
        print(f"BERT_POS_TAGS: {bert_pos_tags}")
    os.system(
        f'./ask.sh {bert_br_MODEL_PATH} "{bert_pos_tags}" bert br > {temp_file}'
    )
    br_tags_file = open(f"{temp_file}", "r").read()
    br_tags = br_tags_file.split("\n")[-3]
    if not silent:
        print(f"BR TAGS: {br_tags}")
    os.remove(f"{temp_file}")
    ce_query = br_tagging(ce_untagged_query, piped_query, br_tags.split(" "))
    kb_simplified_query, mapping_replace = simplify_english_request(ce_query)
    if not silent:
        print(f"KBs Query: {kb_simplified_query}")

    if src_tgt_MODEL_PATH:
        # Use NMT model to translate the KB-simplified CE english request to KB-simplified request
        os.system(
            f'./ask.sh {src_tgt_MODEL_PATH} "{kb_simplified_query}" {src} {tgt} > {temp_file}'
        )
        datalog_file = open(f"{temp_file}", "r").read()
        os.remove(f"{temp_file}")
        datalog_query = datalog_file.split("\n")[-3]
        # Replace back
        mapping_replace = {
            mapping_replace[key]: do_replacements(key, {" ": "_"})
            for key in mapping_replace.keys()
        }
        print(mapping_replace)
        datalog_query = do_replacements_except(
            datalog_query, mapping_replace, " ", exceptions_for_replace
        )

        if not silent:
            print(f"Prev. query: {datalog_query}")
        return datalog_query
    return ce_query