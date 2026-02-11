# RCSB API Utility Library

A Python toolkit designed to simplify interactions with the **RCSB API**.
This library provides an alternative to rcsb-api and supports **autocompletion**.
Currently only the data api has been implemented (ie find thing given query).

## TODO
- implement search api (in process of merge)
- implement batch processing

## Installation

### Prerequisites
* Python >= 3.10
* `requests`
* optional: `numba`

### Setup
`pip install git+https://github.com/vivek-booshan/rcsb.git`

or

`uv add git+https://github.com/vivek-booshan/rcsb.git`

## Usage

#### Query Argument Types Key

| GraphQL Type | Python Equivalent | Description |
| :--- | :--- | :--- |
| `String!` | `str` | A required single string (e.g., "4HHB") |
| `Int!` | `int` | A required single integer (e.g., 12345) |
| `[String]!` | `list[str]` | A required list of strings |
| `[String!]!` | `list[str]` | A required list of strings (elements cannot be null) |


#### Core Structural Queries
Primary entry points for fetching metadata for entries and their chemical components.

| Method | Arguments | Key Mapping |
| :--- | :--- | :--- |
| **entry** | `entry_id: String!` | Individual PDB ID |
| **entries** | `entry_ids: [String!]!` | List of PDB IDs |
| **chem_comp** | `comp_id: String!` | Chemical component ID (e.g., "HEM") |
| **chem_comps** | `comp_ids: [String]!` | List of chemical component IDs |


#### Polymer & Non-Polymer Entities
Entities represent the unique chemical molecules in the structure (e.g., a specific protein chain or a ligand type).

| Method | Arguments | Identifier Format |
| :--- | :--- | :--- |
| **polymer_entity** | `entry_id: String!`, `entity_id: String!` | `4HHB`, `1` |
| **polymer_entities** | `entity_ids: [String!]!` | `["4HHB_1", "1AZW_1"]` |
| **nonpolymer_entity** | `entry_id: String!`, `entity_id: String!` | `4HHB`, `3` |
| **nonpolymer_entities** | `entity_ids: [String!]!` | `["4HHB_3"]` |
| **branched_entity** | `entry_id: String!`, `entity_id: String!` | Carbohydrates/Branched polymers |
| **branched_entities** | `entity_ids: [String!]!` | List of branched entities |


#### Instances (Chains)
Instances represent the specific occurrences of entities in the asymmetric unit (the "chains").

| Method | Arguments | Identifier Format |
| :--- | :--- | :--- |
| **polymer_entity_instance** | `entry_id: String!`, `asym_id: String!` | `4HHB`, `A` |
| **polymer_entity_instances** | `instance_ids: [String]!` | `["4HHB.A", "4HHB.B"]` |
| **nonpolymer_entity_instance** | `entry_id: String!`, `asym_id: String!` | Ligand chain ID |
| **nonpolymer_entity_instances** | `instance_ids: [String]!` | List of ligand chain IDs |
| **branched_entity_instance** | `entry_id: String!`, `asym_id: String!` | Carbohydrate chain ID |
| **branched_entity_instances** | `instance_ids: [String]!` | List of carbohydrate chain IDs |


#### Biological Assemblies & Interfaces
Queries for the quaternary structure and the contact surfaces between molecules.

| Method | Arguments |
| :--- | :--- |
| **assembly** | `entry_id: String!`, `assembly_id: String!` |
| **assemblies** | `assembly_ids: [String]!` |
| **interface** | `entry_id: String!`, `assembly_id: String!`, `interface_id: String!` |
| **interfaces** | `interface_ids: [String!]!` |


#### External Mappings & Groups
Data linked to external databases or grouped by sequence/structural similarity.

| Method | Arguments | Description |
| :--- | :--- | :--- |
| **uniprot** | `uniprot_id: String!` | UniProt Accession (e.g., "P68871") |
| **pubmed** | `pubmed_id: Int!` | PubMed ID for primary citation |
| **polymer_entity_group** | `group_id: String!` | Entity group ID |
| **polymer_entity_groups** | `group_ids: [String]!` | List of entity group IDs |
| **entry_group** | `group_id: String!` | Entry group ID |
| **entry_groups** | `group_ids: [String]!` | List of entry group IDs |
| **group_provenance** | `group_provenance_id: String!` | Methodology metadata |
---

### Building Custom GraphQL Queries
Thanks to the code generation script, every relevant class from the official [data_api_search.json](https://github.com/rcsb/py-rcsb-api/blob/83368df13112374643e02c6c04a6fea3a67ad683/rcsbapi/data/resources/data_api_schema.json) is implemented in `data.py`, which provides easy determination of valid options through autocomplete.

Fair warning: the code has not been thoroughly checked for bugs, but the majority of errors are easily traceable.

To create a query, use QueryBuilder (returns a new query object). The first "core" class requires a kwarg that follows the rcsb api semantics.
The `.end` property just moves the query back to the previous parent. The last trailing set of `.end` are unnecessary to render correctly.
```python
from rcsb.data import QueryBuilder as QB

query = (QB().entry(entry_id="$id") # NOTE: kwarg matches entry(entry_id: String!)
    .polymer_entities
        .rcsb_id
        .entity_poly
            .pdbx_seq_one_letter_code_can
            .end
        .rcsb_target_cofactors
            .binding_assay_value
            .binding_assay_value_type
            .cofactor_SMILES
            .end # move back up to polymer_entities
        .uniprots
            .rcsb_id
            .end # move back up to polymer_entities
        .rcsb_polymer_entity_align
            .aligned_regions
                .entity_beg_seq_id
                .ref_beg_seq_id
                .end # move back up to rcsb_polymer_entity_align
            .end # move back up to polymer_entities
        .polymer_entity_instances
            .rcsb_polymer_instance_feature
                .name
                .feature_positions
                    .beg_comp_id
                    .beg_seq_id
                .end # optional; move back up to rcsb_polymer_instance_feature
            .end # optional; move back up to polymer_entitites
        .end # optional; move back to query
    )
```

### Visualizing Queries
The `.render()` method returns a string of the final query
```python
print(query.render())
```
```
query structure($id: String!) {
  entry(entry_id: $id) {
    polymer_entities {
      rcsb_id
      entity_poly {
        pdbx_seq_one_letter_code_can
      }
      rcsb_target_cofactors {
        binding_assay_value
        binding_assay_value_type
        cofactor_SMILES
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
          feature_positions {
            beg_comp_id
            beg_seq_id
          }
        }
      }
    }
  }
}
```
### Submitting Queries
There are two ways to submit a query, either with `.submit` or the static method `QueryNode.execute`. The only difference is that `.submit` generates the query string on each call, while `.execute` does not build the whole query tree and instead expects the query string to be provided. This provides both straight-forward interactive use with `.submit` and multiple submission usage with `.execute`.

`query.submit` and `QueryNode.execute` expect a kwarg argument that matches the '$var' used when building the query.

#### .submit()
```python
query.submit(id="1b38") # errors if any keyword other than id is used because '$id' was used in query
```

#### .execute()
```python
from rcsb.data import Query # Inherits QueryNode, use either for execute

target_ids = ["1b38", "2zta", "9c61", "5yjk", "1wla", ...]

rendered_query= query.render()

## Example 1: For loop
results = []
for pdb_id in target_ids:
    results.append(Query.execute(rendered_query, id=pdb_id)) # errors if kwarg != 'id'
```

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from rcsb.data import Query

rendered_query = query.render()
target_ids = ["1b38", "6mdr", "5dwy"]

results = []
MAX_WORKERS = os.cpu_count()
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {
        executor.submit(
            Query.execute,
            rendered_query, # must be rendered outside, as render() modifies self
            **{"id": pdb_id.lower()}
        ): pdb_id.lower() for pdb_id in target_ids
    }

for future in as_completed(futures):
    pdb_id = futures[future]
    try:
        data = future.result()
        results.append(data)
    except Exception as e:
        print(f"{pdb_id} generated an exception: {e}")

print(results)
```
```python
from joblib import Parallel, delayed
from rcsb.data import Query

results = Parallel(n_jobs=-1)(
    delayed(Query.execute)(rendered_query, {"id": pdb_id}) 
    for pdb_id in target_ids
)
```

### Accessing results
`submit` and `execute` both return nested dictionaries. A simple and convenient unwrapper `unwrap_query` is provided for quick usage.

```python
result = query.submit(id="1b38")

unwrap_query(result, ["entry"]) # same as result.get("entry")

unwrap_query(result, ["entry", "polymer_entities", "rcsb_target_cofactors"]) # returns list of cofactors from query

# UserWarning: Ambiguous data at depth 3 for key 'cofactor_SMILES': List contains 220 items. Defaulting to the first item. Set strict=True to raise an error instead.
unwrap_query(result, ["entry", "polymer_entities", "rcsb_target_cofactors", "cofactor_SMILES"])

# ValueError: Ambiguous data at depth 3: List contains multiple items but unwrap_query expected a single object or scalar.
unwrap_query(result, ["entry", "polymer_entities", "rcsb_target_cofactors", "cofactor_SMILES"], strict=True)

unwrap_query(result, ["entry", "polymer_entities", "entity_poly", "pdbx_one_seq_letter_code_can"]) # unwraps single item list (entity_poly); returns sequence
```

## Processing

The `process` method is a high-level orchestrator that combines **automatic batching**, **concurrent Network I/O**, and **parallelized parsing** to fetch and process large volumes of structural data from the RCSB PDB GraphQL API into data ready formats. It takes
- inputs: inputs of the query (`list[str]` for single inputs and `list[dict[str, str]]` for multiple inputs like the interface query)
- func: callable function to process the query for a single submission
- const_kwargs: submission agnostic arguments that remain the same for all queries
- iter_kwargs: submission specific arguments (eg, the example function takes the pdb_id of each entry as an additional input)
---

### Advanced Example: Deep Data Extraction for Affinity Prediction. 

For a simple affinity prediction pipeline, a research often wants pdb sequences, ligands, affinities, and the affinity types (IC50, EC50, Kd, Ki, etc). In this example, we fetch polymer sequences, UniProt alignments, ligand interaction sites, and cofactor SMILES with binding affinities.

### Define the Query
```python
from rcsb.data import QueryBuilder as QB
query = (QB()
    .entries(entry_ids="$ids")
    .polymer_entities
        .rcsb_id
        .entity_poly.pdbx_seq_one_letter_code_can.end
        .rcsb_target_cofactors
            .binding_assay_value
            .binding_assay_value_type
            .cofactor_SMILES
            .end
        .uniprots.rcsb_id.end
        .rcsb_polymer_entity_align
            .aligned_regions.entity_beg_seq_id.ref_beg_seq_id.end
            .end
        .polymer_entity_instances
            .rcsb_polymer_instance_feature
                .name
                .feature_positions.beg_comp_id.beg_seq_id.end
                .end
            .end
        .end
    .nonpolymer_entities
        .nonpolymer_comp.chem_comp.id.end.end
        .nonpolymer_entity_instances
            .rcsb_nonpolymer_instance_validation_score.is_subject_of_investigation.end
            .end
        .end
    .end
)
```

### Define the Processing Function
```python
from rcsb import unwrap_query
def process_single_entry(entry, pdb_id: str, ligand: str = None, filter_affinity_nulls: bool = True):
    if entry is None:
        return None

    # Identify 'Subject of Investigation' Ligand
    subject_of_investigation = ligand
    if subject_of_investigation is None:
        for entity in entry.get("nonpolymer_entities") or []:
            valid_score = unwrap_query(entity, ["nonpolymer_entity_instances", "rcsb_nonpolymer_instance_validation_score"])
            if valid_score and valid_score[0].get("is_subject_of_investigation") == 'Y':
                subject_of_investigation = entity.get("nonpolymer_comp", {}).get("chem_comp", {}).get("id")

    # Get Canonical Sequence
    poly = entry.get("polymer_entities", [{}])[0]
    canonical_seq = unwrap_query(poly, ["entity_poly", "pdbx_seq_one_letter_code_can"])

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


    # Extract Cofactors & Affinities
    cofactors = poly.get("rcsb_target_cofactors") or []
    if filter_affinity_nulls:
        cofactors = [c for c in cofactors if c.get("binding_assay_value") is not None]

    return {
        "pdb_id": pdb_id,
        "seq": canonical_seq,
        "uniprot": (uniprot_id, uniprot_idx, uniprot_offset)
        "binding_sites": interactions,
        "smiles": tuple(c["cofactor_SMILES"] for c in cofactors),
        "affinity": tuple(c["binding_assay_value"] for c in cofactors),
        "ligand": subject_of_investigation
    }
```

### Submit the process
```python
pdb_ids = [...]
results = query.process(
    inputs=pdb_ids, 
    func=process_single_entry, 
    iter_kwargs={"pdb_id": pdb_ids},
    max_workers=10
)
```



