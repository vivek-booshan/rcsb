# RCSB API Utility Library

A Python toolkit designed to streamline interactions with the **RCSB Protein Data Bank (PDB)** via their GraphQL API. 
This library provides high-level abstractions for fetching structural data, mapping UniProt IDs, performing batched operations, and generating sequence mutants.

## Installation

### Prerequisites
* Python >= 3.10
* `requests`

### Setup
`pip install git+https://github.com/vivek-booshan/rcsb.git`

or

`uv add git+https://github.com/vivek-booshan/rcsb.git`

## Usage

### Custom GraphQL Queries
RCSB queries can be built using custom syntax or directly built via the `.raw()` method. Because the `QueryBuilder` class is not immutable,
`.clone()` method should be used to to ensure that the original query object remains unchanged when creating a new, modified version of a query.

```python
# example.py
from rcsb.graphql import QueryBuilder, submit_query

qb = QueryBuilder()
query = (qb.clone()
    .enter("polymer_entities") 
        .add("rcsb_id") 
        .enter("rcsb_polymer_entity_annotation")
            .add("annotation_id", "type")
        .end()
    .end() # nodes must be enclosed with .end(). This is literally just a '}', but it's robust enough and greppable
)
```
Using `query.render()` will show the query string. The above generates the following query

```python
query structure($id: String!) {
  entry(entry_id: $id) {
    polymer_entities {
      rcsb_id
      rcsb_polymer_entity_annotation {
        annotation_id
        type
      }
    }
  }
}
```

Separate query can be built with the existing builder object, but note that the `.clone()` method must be used.
```python
# example.py

new_query = (qb.clone()
    .raw("""
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
    """)
)
```
The above returns the following query
```python
"""
query structure($id: String!) {
  entry(entry_id: $id) {
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
```

Queries can be modified. Again, the `.clone` method must be used or otherwise the original query object will be modified. 
```python
modified_query = (query.clone()
    .raw("""
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
    """)
)
```
The above returns the following query 
```python
"""
query structure($id: String!) {
  entry(entry_id: $id) {
    polymer_entities {
      rcsb_id
      rcsb_polymer_entity_annotation {
        annotation_id
        type
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
```

