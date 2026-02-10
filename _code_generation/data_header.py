import textwrap
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Optional, List, Union

RCSB_ARGUMENT_TYPES = {
    "polymer_entity_instance": {"asym_id": "String!", "entry_id": "String!"},
    "chem_comps": {"comp_ids": "[String]!"},
    "nonpolymer_entity_groups": {"group_ids": "[String]!"},
    "polymer_entity_groups": {"group_ids": "[String]!"},
    "interface": {"assembly_id": "String!", "interface_id": "String!", "entry_id": "String!"},
    "nonpolymer_entities": {"entity_ids": "[String!]!"},
    "polymer_entities": {"entity_ids": "[String!]!"},
    "polymer_entity": {"entity_id": "String!", "entry_id": "String!"},
    "entry_group": {"group_id": "String!"},
    "pubmed": {"pubmed_id": "Int!"},
    "assembly": {"assembly_id": "String!", "entry_id": "String!"},
    "branched_entity_instances": {"instance_ids": "[String]!"},
    "group_provenance": {"group_provenance_id": "String!"},
    "polymer_entity_instances": {"instance_ids": "[String]!"},
    "interfaces": {"interface_ids": "[String!]!"},
    "nonpolymer_entity_group": {"group_id": "String!"},
    "assemblies": {"assembly_ids": "[String]!"},
    "branched_entity": {"entity_id": "String!", "entry_id": "String!"},
    "polymer_entity_group": {"group_id": "String!"},
    "branched_entity_instance": {"asym_id": "String!", "entry_id": "String!"},
    "nonpolymer_entity_instance": {"asym_id": "String!", "entry_id": "String!"},
    "chem_comp": {"comp_id": "String!"},
    "entry": {"entry_id": "String!"},
    "entries": {"entry_ids": "[String!]!"},
    "entry_groups": {"group_ids": "[String]!"},
    "branched_entities": {"entity_ids": "[String!]!"},
    "uniprot": {"uniprot_id": "String!"},
    "nonpolymer_entity_instances": {"instance_ids": "[String]!"},
    "nonpolymer_entity": {"entity_id": "String!", "entry_id": "String!"}
}


# --- Query Logic ---

class QueryNode:
    def __init__(self, name=None, parent=None, arguments=None):
        self._name = name
        self._parent = parent
        self._children = []
        self._arguments = arguments or {}

    def _enter(self, name, node_class, **kwargs):
        # Deduplication: Return existing node if already requested
        for child in self._children:
            if child._name == name and isinstance(child, node_class):
                child._arguments.update(kwargs)
                return child
        
        # Create new typed node
        new_node = node_class(name=name, parent=self, arguments=kwargs)
        self._children.append(new_node)
        return new_node

    @property
    def end(self):
        """Navigates back to the parent node."""
        return self._parent if self._parent else self

    def render(self, query_name="structure"):
        root = self
        while root._parent:
            root = root._parent

        variable_map = {}
        
        for child in root._children:
            # Skip if it's just a string/scalar leaf
            if not hasattr(child, "_name"): 
                continue

            known_args = RCSB_ARGUMENT_TYPES.get(child._name, {})

            for arg_name, arg_value in child._arguments.items():
                if isinstance(arg_value, str) and arg_value.startswith("$"):
                    clean_var_name = arg_value[1:] # remove $
                    gql_type = known_args.get(arg_name, "String!")
                    variable_map[clean_var_name] = gql_type

        var_header = ""
        if variable_map:
            defs = [f"${name}: {type_def}" for name, type_def in sorted(variable_map.items())]
            var_header = f"({', '.join(defs)})"

        fields = root._render_node(indent=2)
        return f"query {query_name}{var_header} {{\n{fields}\n}}"

    def _render_node(self, indent=0):
        pad = " " * indent
        if self._name is None: # Root
            parts = [c._render_node(indent) for c in self._children]
            return "\n".join(filter(None, parts))

        # Format Arguments
        name_part = self._name
        if self._arguments:
            args = []
            for k, v in self._arguments.items():
                if isinstance(v, str) and v.startswith("$"):
                    args.append(f'{k}: {v}')
                elif isinstance(v, str):
                    args.append(f'{k}: "{v}"')
                else:
                    args.append(f"{k}: {v}")

            name_part = f"{self._name}({', '.join(args)})"

        if not self._children:
            # Leaf node (Scalar)
            return f"{pad}{name_part}"
        
        # Object node
        inner = [c._render_node(indent + 2) for c in self._children]
        # Filter empty blocks (Ghost nodes)
        inner = list(filter(None, inner))
        if not inner:
            return "" 
            
        return f"{pad}{name_part} {{\n" + "\n".join(inner) + f"\n{pad}}}"

    @staticmethod
    def execute(rendered_query: str, **variables):
        """Executes a rendered GraphQL query against the RCSB Data API."""
        response = requests.post(
            "https://data.rcsb.org/graphql",
            json={
            	"query": rendered_query,
            	"variables": variables or {}
            },
        )
        response.raise_for_status()
    
        return response.json().get("data", {})

    def submit(self, **variables):
        """Renders and executes the stored query.
        Use `QueryNode.execute` if running multiple submissions."""
        return self.execute(self.render(), **variables)

    def process(self, inputs: list, func: callable, batch_size: int = None, max_workers: int = None, const_kwargs: dict = {}, iter_kwargs: dict = {}):
        """Execute and process batched GraphQL queries with threads. This is intended for large inputs. 

        Args:
            - query: The GraphQL query
            - inputs: Data to batch. Can be `List[str]` for single variables or 
                `List[Dict[str, str]]` for multiple variables (e.g., interface IDs).
            - func: Callback function to parse each entry. Signature: `func(entry, **kwargs)`.
            - batch_size: Number of inputs per API request. Defaults to 200 if batch_size = None.
            - max_workers: Max concurrent threads for I/O and parsing.
            - const_kwargs: Fixed arguments passed to `func` for every entry.
            - iter_kwargs: Mapping of names to iterables of size `len(inputs)` for entry-specific metadata.

        Returns:
            A list of results returned by `func`
        """

        n_inputs = len(inputs)

        child = self._children[0]
        result_key = child._name
        if result_key not in RCSB_ARGUMENT_TYPES.keys():
            raise ValueError("""Result key could not be determined.
                             Child is {child._name}. Ensure the query is ".end"ed properly.""")

        batch_vars = []
        for arg_value in child._arguments.values():
            if isinstance(arg_value, str) and arg_value.startswith("$"):
                batch_vars.append(arg_value[1:])  # Strip "$"
                break
    
        if not batch_vars:
            raise ValueError(
                f"No GraphQL variable (starting with '$') found in arguments for '{child._name}'. "
                "Cannot determine which variable to use for batching."
            )
    
        for k, v in iter_kwargs.items():
            if len(v) != n_inputs:
                raise ValueError(f"List argument '{k}' len {len(v)} != inputs len {n_inputs}")

        if batch_size is None:
            batch_size = n_inputs if n_inputs < 200 else 200

        def handle_batch(start_idx: int):
            end_idx = start_idx + batch_size
            batch_slice = inputs[start_idx:end_idx]

            submit_kwargs = {}
            if len(batch_vars) == 1:
                submit_kwargs[batch_vars[0]] = batch_slice
            else:
                for var in batch_vars:
                    submit_kwargs[var] = [item[var] for item in batch_slice]

            response = self.submit(**submit_kwargs)
            entries = response.get(result_key, [])

            batch_out = []
            for idx, entry in enumerate(entries):
                item_kwargs = {**const_kwargs}
                for k, v in iter_kwargs.items():
                    item_kwargs[k] = v[start_idx + idx]
    
                batch_out.append(func(entry, **item_kwargs))
            return batch_out

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            indices = range(0, n_inputs, batch_size)
            future_to_batch = {executor.submit(handle_batch, i): i for i in indices}

        final_results = []    
        for future in as_completed(future_to_batch):
            try:
                final_results.extend(future.result())
            except Exception as e:
                print(f"Error in batch starting at {future_to_batch[future]}: {e}")

        return final_results

# --- Generated Schema Classes ---
