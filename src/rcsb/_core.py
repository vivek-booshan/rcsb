import requests
from dataclasses import dataclass 
from ._query import unwrap_query
from ._mutate_util import _mutate_sequence

GRAPHQL_URL = "https://data.rcsb.org/graphql"

GRAPHQL_QUERY = """
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
      rcsb_polymer_entity_align {
          aligned_regions {
              entity_beg_seq_id
              ref_beg_seq_id
          }
      }

      polymer_entity_instances {
        rcsb_polymer_instance_feature {
          name
          type
          feature_positions {
            beg_comp_id
            beg_seq_id
          }
        }
      }

      rcsb_target_cofactors {
        binding_assay_value
        binding_assay_value_type  
        cofactor_SMILES
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

@dataclass
class rcsbEntry:
    pdb_id: str
    seq: str
    uniprot_offset: int
    uniprot_index: int
    uniprot_id: str
    binding_site_positions: set[int] | None
    smiles: list[str] | None
    affinity: list[str] | None
    affinity_type: list[str] | None
    ligand: str | None
    mutants: dict | None # = field(init=True)

class QueryPathError(Exception):
    def __init__(self, message, depth, key):
        super().__init__(message)
        self.depth = depth
        self.key = key
   
   
def _mutate_entry(entry, ligand: str = None, positions: tuple[int] = None, seed: int=67, poly='A', inplace: bool = False):
    if positions is not None and ligand is not None:
        raise ValueError("Must specify either 'ligand' or 'positions' only.")

    if positions is not None:
        bsp = positions
        entry.binding_site_positions = bsp
    else:
        if ligand is None and entry.ligand is not None:
            ligand = entry.ligand
        elif (ligand is not None and (f"ligand {ligand.upper()}" in entry.binding_site_positions.keys())):
            entry.ligand = ligand.upper()
        else:
            raise ValueError(f"ligand {ligand.upper()} not valid key.\nValid keys are {entry.binding_site_positions.keys()}")
        bsp = entry.binding_site_positions[f"ligand {ligand.upper()}"]

    mutants =_mutate_sequence(entry.seq, bsp, seed, poly)
    if inplace:
        entry.mutants = mutants
        return

def _mutate_multiple_entries(*args, **kwargs):
    raise NotImplementedError(
        "mutate_multiple_entries is not implemented. "
        "Use batched.get_entries(pdb_ids, auto_mutate=True) instead."
    )

def _find_entity_by_rcsb_id(queried_polymer_entities, pdb_id, rcsb_id="1"):
    for entity in queried_polymer_entities:
        if entity.get("rcsb_id") == f"{pdb_id.upper()}_{rcsb_id}":
            return entity

def _find_entity_by_first(queried_polymer_entities):
    return queried_polymer_entities[0]


def _find_entity_by_subject(queried_polymer_entities, subject_of_investigation):
    for entity in queried_polymer_entities:
        for feature in unwrap_query(entity,
                                path=["polymer_entity_instances", "rcsb_polymer_instance_feature"]):
            if feature.get("type") != "LIGAND_INTERACTION":
                continue

            if feature.get("name") == f"ligand {subject_of_investigation.upper()}":
                return entity

            print(feature.get("type"), feature.get("name"))
    return None


def _find_entity(queried_polymer_entities, search_method, pdb_id, subject_of_investigation):
    if queried_polymer_entities is None:
        print("No polymer entities found")
        return None

    match search_method:
        case "rcsb_id":
            return _find_entity_by_rcsb_id(queried_polymer_entities, pdb_id)
        case "ligand":
            # if subject_of_investigation is None:
            #     return None
            return _find_entity_by_subject(queried_polymer_entities, subject_of_investigation)
        case "first":
            return _find_entity_by_first(queried_polymer_entities)
        case _:
            raise ValueError(f"Invalid search method {search_method}")
            # return _find_entity_by_first(queried_polymer_entities)

def _get_entry(
    pdb_id: str,
    ligand: str=None,
    search_method="first",
    filter_affinity_nulls: bool = True,
    auto_mutate: bool =False,
    **mutation_kwargs
):
    pdb_id = pdb_id.lower()
    query = (
        requests.post(
            GRAPHQL_URL,
            json={"query": GRAPHQL_QUERY, "variables": {"id": pdb_id}}
        )
        .json()
        .get("data")
        .get("entry")
    )
    if query is None:
        print(f"Query not found for {pdb_id}. Setting value to None")
        return None

    nonpolymer_entities = query.get("nonpolymer_entities")
    
    # subject of investigation
    subject_of_investigation = None
    if ligand is not None:
        subject_of_investigation = ligand
    else:
        for entity in nonpolymer_entities or tuple():
            is_subject_of_investigation = unwrap_query(entity,
                                                  path=[
                                                      "nonpolymer_entity_instances",
                                                      "rcsb_nonpolymer_instance_validation_score",
                                                      "is_subject_of_investigation"
                                                  ])
            if is_subject_of_investigation == 'Y':
                subject_of_investigation = entity.get("nonpolymer_comp").get("chem_comp").get("id")
    
    # select polymer entity with id {PDBID}_1
    polymer_entity = _find_entity(query.get("polymer_entities"), search_method, pdb_id, subject_of_investigation)
    canonical_seq = unwrap_query(polymer_entity, ["entity_poly", "pdbx_seq_one_letter_code_can"])

    uniprot_offset = None
    uniprot_idx = None
    try:
        uniprot_id = unwrap_query(polymer_entity, ["uniprots", "rcsb_id"])
        aligned_regions = unwrap_query(polymer_entity, ["rcsb_polymer_entity_align", "aligned_regions"])
        uniprot_offset = unwrap_query(aligned_regions, ["entity_beg_seq_id"]) - 1
        uniprot_idx = unwrap_query(aligned_regions, ["ref_beg_seq_id"])
    except Exception as e:
        print(f"Warning: {pdb_id} uniprot detection failed with {type(e)} {e}")

    ## binding site positions
    ligand_interactions = {}
    for instance_feature in unwrap_query(polymer_entity,
                                    path=["polymer_entity_instances", "rcsb_polymer_instance_feature"]):
        if instance_feature.get("type") != "LIGAND_INTERACTION":
            continue
        if ligand is not None and instance_feature.get("name") != f"ligand {ligand.upper()}":
            continue

        name = instance_feature.get("name")
        if name not in ligand_interactions:
            ligand_interactions[name] = set()

        positions = instance_feature.get("feature_positions")
        for p in positions:
            ligand_interactions[name].add(p.get("beg_seq_id") - 1)

    ## cofactor smiles
    cofactors = polymer_entity.get("rcsb_target_cofactors")
    if filter_affinity_nulls and cofactors is not None:
        cofactors = [cofactor for cofactor in cofactors if cofactor.get("binding_assay_value") is not None] 

    smiles = list()
    affinity = list()
    affinity_type = list()
    for cofactor in cofactors or tuple():
        smiles.append(cofactor["cofactor_SMILES"])
        affinity.append(cofactor["binding_assay_value"])
        affinity_type.append(cofactor["binding_assay_value_type"])

    mutants = None
    if auto_mutate:
        try:
            if subject_of_investigation is None:
                raise ValueError("No subject of investigation detected")
            mutants = _mutate_sequence(canonical_seq, ligand_interactions, **mutation_kwargs)
        except Exception as e:
            print(f"""Warning: {pdb_id} auto-mutation failed with {type(e)} {e}.
                  Valid keys are {ligand_interactions.keys()}.
                  Setting primary ligand to NoneType.""")

    return rcsbEntry(
        pdb_id=pdb_id,
        seq=canonical_seq,
        uniprot_offset=uniprot_offset,
        uniprot_index=uniprot_idx,
        uniprot_id=uniprot_id,
        binding_site_positions=ligand_interactions,
        smiles=tuple(smiles),
        affinity=tuple(affinity),
        affinity_type=tuple(affinity_type),
        ligand=subject_of_investigation,
        mutants=mutants
    )

def _get_entry_by_sequence(
    pdb_id: str,
    ref_seq: str,
    ligand: str=None,
    search_method="first",
    filter_affinity_nulls: bool = True,
    auto_mutate: bool =False,
    **mutation_kwargs
):
    pdb_id = pdb_id.lower()
    query = (
        requests.post(
            GRAPHQL_URL,
            json={"query": GRAPHQL_QUERY, "variables": {"id": pdb_id}}
        )
        .json()
        .get("data")
        .get("entry")
    )
    if query is None:
        print(f"Query not found for {pdb_id}. Setting value to None")
        return None

    nonpolymer_entities = query.get("nonpolymer_entities")
    
    # subject of investigation
    subject_of_investigation = None
    if ligand is not None:
        subject_of_investigation = ligand
    else:
        for entity in nonpolymer_entities or tuple():
            is_subject_of_investigation = unwrap_query(entity,
                                                  path=[
                                                      "nonpolymer_entity_instances",
                                                      "rcsb_nonpolymer_instance_validation_score",
                                                      "is_subject_of_investigation"
                                                  ])
            if is_subject_of_investigation == 'Y':
                subject_of_investigation = entity.get("nonpolymer_comp").get("chem_comp").get("id")
    
    # select polymer entity with id {PDBID}_1
    entity_num = 0
    max_similarity = 0
    for i, entity in enumerate(query.get("polymer_entities")):
        seq = unwrap_query(entity, ["entity_poly", "pdbx_seq_one_letter_code_can"])
        similarity = _lcs_similarity(seq, ref_seq)
        if similarity > max_similarity:
            max_similarity = similarity
            entity_num = i

    try:
        polymer_entity = query.get("polymer_entities")[entity_num]
    except Exception as e:
        print(e)
        return None
    
    canonical_seq = unwrap_query(polymer_entity, ["entity_poly", "pdbx_seq_one_letter_code_can"])

    uniprot_offset = None
    uniprot_idx = None
    uniprot_id = None
    try:
        uniprot_id = unwrap_query(polymer_entity, ["uniprots", "rcsb_id"])
        aligned_regions = unwrap_query(polymer_entity, ["rcsb_polymer_entity_align", "aligned_regions"])
        uniprot_offset = unwrap_query(aligned_regions, ["entity_beg_seq_id"]) - 1
        uniprot_idx = unwrap_query(aligned_regions, ["ref_beg_seq_id"])
    except Exception as e:
        print(f"Warning: {pdb_id} uniprot detection failed with {type(e)} {e}")

    ## binding site positions
    ligand_interactions = {}
    for instance_feature in unwrap_query(polymer_entity,
                                    path=["polymer_entity_instances", "rcsb_polymer_instance_feature"]):
        if instance_feature.get("type") != "LIGAND_INTERACTION":
            continue
        if ligand is not None and instance_feature.get("name") != f"ligand {ligand.upper()}":
            continue

        name = instance_feature.get("name")
        if name not in ligand_interactions:
            ligand_interactions[name] = set()

        positions = instance_feature.get("feature_positions")
        for p in positions:
            ligand_interactions[name].add(p.get("beg_seq_id") - 1)

    ## cofactor smiles
    cofactors = polymer_entity.get("rcsb_target_cofactors")
    if filter_affinity_nulls and cofactors is not None:
        cofactors = [cofactor for cofactor in cofactors if cofactor.get("binding_assay_value") is not None] 

    smiles = list()
    affinity = list()
    affinity_type = list()
    for cofactor in cofactors or tuple():
        smiles.append(cofactor["cofactor_SMILES"])
        affinity.append(cofactor["binding_assay_value"])
        affinity_type.append(cofactor["binding_assay_value_type"])

    mutants = None
    if auto_mutate:
        try:
            if subject_of_investigation is None:
                raise ValueError("No subject of investigation detected")
            mutants = _mutate_sequence(canonical_seq, ligand_interactions, **mutation_kwargs)
        except Exception as e:
            print(f"""Warning: {pdb_id} auto-mutation failed with {type(e)} {e}.
                  Valid keys are {ligand_interactions.keys()}.
                  Setting primary ligand to NoneType.""")

    return rcsbEntry(
        pdb_id=pdb_id,
        seq=canonical_seq,
        uniprot_offset=uniprot_offset,
        uniprot_index=uniprot_idx,
        uniprot_id=uniprot_id,
        binding_site_positions=ligand_interactions,
        smiles=tuple(smiles),
        affinity=tuple(affinity),
        affinity_type=tuple(affinity_type),
        ligand=subject_of_investigation,
        mutants=mutants
    )


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

def _get_uid(pdb_id, search_method="first"):
    pdb_id = pdb_id.lower()
    query = (
        requests.post(
            GRAPHQL_URL,
            json={"query": UNIPROT_QUERY, "variables": {"id": pdb_id}}
        )
        .json()
        .get("data")
        .get("entry")
    )
    if query is None:
        print(f"Query not found for {pdb_id}. Setting value to None")
        return None

    nonpolymer_entities = query.get("nonpolymer_entities")
    subject_of_investigation = None
    for entity in nonpolymer_entities or tuple():
        is_subject_of_investigation = unwrap_query(entity,
                                              path=[
                                                  "nonpolymer_entity_instances",
                                                  "rcsb_nonpolymer_instance_validation_score",
                                                  "is_subject_of_investigation"
                                              ])
        if is_subject_of_investigation == 'Y':
            subject_of_investigation = entity.get("nonpolymer_comp").get("chem_comp").get("id")

    polymer_entity = _find_entity(query.get("polymer_entities"), search_method, pdb_id, subject_of_investigation)
    uniprot_id = None
    try:
        uniprot_id = unwrap_query(polymer_entity, ["uniprots", "rcsb_id"])
    except Exception as e:
        print(e)
    return uniprot_id

def _lcs_length(seq1, seq2):
    n, m = len(seq1), len(seq2)
    dp = [[0]*(m+1) for _ in range(n+1)]
    for i in range(n):
        for j in range(m):
            if seq1[i] == seq2[j]:
                dp[i+1][j+1] = dp[i][j] + 1
            else:
                dp[i+1][j+1] = max(dp[i][j+1], dp[i+1][j])
    return dp[n][m]

def _lcs_similarity(seq1, seq2):
    return _lcs_length(seq1, seq2) / max(len(seq1), len(seq2))

def _get_uid_by_sequence(pdb_id, ref_seq, search_method="first"):
    pdb_id = pdb_id.lower()
    query = (
        requests.post(
            GRAPHQL_URL,
            json={"query": UNIPROT_QUERY, "variables": {"id": pdb_id}}
        )
        .json()
        .get("data")
        .get("entry")
    )
    if query is None:
        print(f"Query not found for {pdb_id}. Setting value to None")
        return None
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
        uniprot_id = unwrap_query(query.get("polymer_entities")[entity_num], ["uniprots", "rcsb_id"])
    except Exception as e:
        print(e)
    return uniprot_id

if __name__ == "__main__":

    def _2():
        entry = _get_entry("6luj", auto_mutate=True)
        # print(entry)
        # mutate_entry(entry, "so4", inplace=True)
        print(entry)

    def _3():
        entry = _get_entry("6woj")
        print(entry)
        entry = _get_entry("5rlh")
        print(entry)

    def _mutate_bsp():
        entry = _get_entry("6lu7")
        entry.mutate_sequence(positions=(41, 145))
        print(entry)

    def _search_method():
        methods = ("first", "rcsb_id", "ligand")
        for method in methods:
            # entry = _get_entry("4yhz")
            entry = _get_entry("1a5h", search_method=method)
            print(entry)
            print()

    # _3()
    # _2()
    # _4()
    # _search_method()
    # print(get_uniprot_by_sequence(
    #       "1aqc",
    #       "MEDLIDGIIFAANYLGSTQLLSDKTPSKNVRMMQAQEAVSRIKMAQKLMTEVDLFILTQRIKVLNADTQETMMDHPLRTISYIADIGNIVVLMARRRYKMICHVFESEDAQLIAQSIGQAFSVAYQEFLR")
    #   )
    # print(get_rcsb("6mqm"))
