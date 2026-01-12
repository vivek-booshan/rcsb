import requests
import warnings
from ._query import unwrap_query
from ._fetch import _find_entity

try:
    from ._lcs_numba import _lcs_length
    USING_NUMBA = True
except ImportError:
    from ._lcs import _lcs_length
    USING_NUMBA = False
    warnings.warn(
        "Numba not found: _lcs_length will use pure Python. "
        "For faster performance, install numba.",
        UserWarning
    )

GRAPHQL_URL = "https://data.rcsb.org/graphql"

# query = RQB()
# (
#     query
#     .enter("polymer_entities")
#         .add("rcsb_id")
#         .enter("entity_poly")
#             .add("pdbx_seq_one_letter_code_can")
#         .end()
#         .enter("uniprots").add("rcsb_id").end()
#     .end()
#     .enter("nonpolymer_entities")
#         .enter("nonpolymer_comp")
#             .enter("chem_comp").add("id").end()
#         .end()
#         .enter("nonpolymer_entity_instances")
#             .enter("rcsb_nonpolymer_instance_validation_score")
#                 .add("is_subject_of_investigation")
#             .end()
#         .end()
#     .end()
# )
# UNIPROT_QUERY = query.render()

UNIPROT_QUERY = """
query structure($id: String!) {
    entry(entry_id: $id) {  
        polymer_entities {
            rcsb_id
            entity_poly {
                pdbx_seq_one_letter_code_can
            }
            uniprots {
                rcsb_id
            }
      	}
		nonpolymer_entities {
            nonpolymer_comp {
                chem_comp {
                    id
                }
            }

            nonpolymer_entity_instances {
                rcsb_nonpolymer_instance_validation_score {
                    is_subject_of_investigation
                }
            }
        }
    }
}
"""


def _uniprot_id(query, pdb_id, search_method):
    nonpolymer_entities = query.get("nonpolymer_entities")
    subject_of_investigation = None
    for entity in nonpolymer_entities or tuple():
        is_subject_of_investigation = unwrap_query(
            entity,
            path=[
                "nonpolymer_entity_instances",
                "rcsb_nonpolymer_instance_validation_score",
                "is_subject_of_investigation",
            ],
        )
        if is_subject_of_investigation == "Y":
            subject_of_investigation = (
                entity.get("nonpolymer_comp").get("chem_comp").get("id")
            )

    polymer_entity = _find_entity(
        query.get("polymer_entities"),
        search_method,
        pdb_id,
        subject_of_investigation
    )
    uniprot_id = None
    try:
        uniprot_id = unwrap_query(polymer_entity, ["uniprots", "rcsb_id"])
    except Exception as e:
        print(e)
    return uniprot_id


def _lcs_similarity(seq1, seq2):
    return _lcs_length(seq1, seq2) / min(len(seq1), len(seq2))


def _uniprot_id_by_sequence(query, pdb_id, ref_seq):
    # print(ref_seq)

    entity_num = 0
    max_similarity = 0
    for i, entity in enumerate(query.get("polymer_entities")):
        # print(i, entity)
        seq = unwrap_query(entity, ["entity_poly", "pdbx_seq_one_letter_code_can"])
        similarity = _lcs_similarity(seq, ref_seq)
        # print(similarity, max_similarity)
        if similarity > max_similarity:
            max_similarity = similarity
            entity_num = i

    # print(entity_num, max_similarity)
    uniprot_id = None
    try:
        uniprot_id = unwrap_query(
            query.get("polymer_entities")[entity_num], ["uniprots", "rcsb_id"]
        )
    except Exception as e:
        print(e)
    return uniprot_id


def get_uid(pdb_id, ref_seq=None, search_method="first") -> str:
    pdb_id = pdb_id.lower()
    query = (
        requests.post(
            GRAPHQL_URL, json={"query": UNIPROT_QUERY, "variables": {"id": pdb_id}}
        )
        .json()
        .get("data")
        .get("entry")
    )
    if query is None:
        print(f"Query not found for {pdb_id}. Setting value to None")
        return None

    if ref_seq is None:
        return _uniprot_id(query, pdb_id, search_method)
    return _uniprot_id_by_sequence(query, pdb_id, ref_seq)

if __name__ == "__main__":
    print(get_uid("1b38", "MEDLIDGIIFAANYLGSTQLLSDKTPSKNVRMMQAQEAVSRIKMAQKLMTEVDLFILTQRIKVLNADTQETMMDHPLRTISYIADIGNIVVLMARRRYKMICHVFESEDAQLIAQSIGQAFSVAYQEFLR"))

