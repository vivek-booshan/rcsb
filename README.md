# RCSB API Utility Library

A Python toolkit designed to simplify interactions with the **RCSB API**.
This library provides an alternative to rcsb-api and supports **autocompletion**.
Currently only the data api has been implemented (ie find thing given query).

## TODO
- remove "String!" hardcode and handle proper rcsb query inputs
- implement search api

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

MAX_WORKERS = os.cpu().count()
results = []
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {
        executor.submit(
            Query.execute, 
            rendered_query, 
            **{"id": pdb_id.lower()}
        ): pdb_id.lower() for pdb_id in target_ids
    }
   
    for future in as_completed(futures):
        pdb_id = futures[future]
        try:
            data = future.result()
            results.append(data)
            print(results)
        except Exception as e:
            print(f"{pdb_id} generated an exception: {e}")
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



