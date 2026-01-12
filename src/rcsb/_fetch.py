import requests
from dataclasses import dataclass
from ._query import _query
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
    binding_site_positions: set[int] | None
    smiles: list[str] | None
    affinity: list[str] | None
    affinity_type: list[str] | None
    ligand: str | None
    mutants: dict | None # = field(init=True)

def _find_entity_by_rcsb_id(queried_polymer_entities, pdb_id, rcsb_id="1"):
    for entity in queried_polymer_entities:
        if entity.get("rcsb_id") == f"{pdb_id.upper()}_{rcsb_id}":
            return entity


def _find_entity_by_first(queried_polymer_entities):
    return queried_polymer_entities[0]


def _find_entity_by_subject(queried_polymer_entities, subject_of_investigation):
    for entity in queried_polymer_entities:
        for feature in _query(entity,
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
            #
def get_rcsb(
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
            is_subject_of_investigation = _query(entity,
                                                  path=[
                                                      "nonpolymer_entity_instances",
                                                      "rcsb_nonpolymer_instance_validation_score",
                                                      "is_subject_of_investigation"
                                                  ])
            if is_subject_of_investigation == 'Y':
                subject_of_investigation = entity.get("nonpolymer_comp").get("chem_comp").get("id")
    
    # select polymer entity with id {PDBID}_1
    polymer_entity = _find_entity(query.get("polymer_entities"), search_method, pdb_id, subject_of_investigation)
    canonical_seq = _query(polymer_entity, ["entity_poly", "pdbx_seq_one_letter_code_can"])

    uniprot_offset = None
    uniprot_idx = None
    try:
        aligned_regions = _query(polymer_entity, ["rcsb_polymer_entity_align", "aligned_regions"])
        uniprot_offset = _query(aligned_regions, ["entity_beg_seq_id"]) - 1
        uniprot_idx = _query(aligned_regions, ["ref_beg_seq_id"])
    except Exception as e:
        print(f"Warning: {pdb_id} uniprot detection failed with {type(e)} {e}")

    ## binding site positions
    ligand_interactions = {}
    for instance_feature in _query(polymer_entity,
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
        binding_site_positions=ligand_interactions,
        smiles=tuple(smiles),
        affinity=tuple(affinity),
        affinity_type=tuple(affinity_type),
        ligand=subject_of_investigation,
        mutants=mutants
    )


