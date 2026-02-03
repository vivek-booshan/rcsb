import json
import re
import keyword

INPUT_FILE = "resources/data_api_schema.json"
OUTPUT_FILE = "data.py"

# from the old api
HEADER = """import textwrap
import requests
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
        \"\"\"Navigates back to the parent node.\"\"\"
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
        return f"query {query_name}{var_header} {{\\n{fields}\\n}}"

    def _render_node(self, indent=0):
        pad = " " * indent
        if self._name is None: # Root
            parts = [c._render_node(indent) for c in self._children]
            return "\\n".join(filter(None, parts))

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
            
        return f"{pad}{name_part} {{\\n" + "\\n".join(inner) + f"\\n{pad}}}"

    @staticmethod
    def execute(rendered_query: str, **variables):
        \"\"\"Executes a rendered GraphQL query against the RCSB Data API.\"\"\"
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
        \"\"\"Renders and executes the stored query.
        Use `QueryNode.execute` if running multiple submissions.\"\"\"
        return self.execute(self.render(), **variables)

# --- Generated Schema Classes ---
"""

def make_code():
    with open(INPUT_FILE, "r") as f:
        data = json.load(f)

    types = find_types(data)
    if not types:
        raise ValueError("Error: No types found in JSON.")

    class_map, parent_map = first_pass(types)

    lines = [HEADER]
    
    query_root = "Query"
    
    for name, t_def in class_map.items():
        parent_cls = parent_map.get(name, "QueryNode")
        if name == query_root:
            parent_cls = "QueryNode"
        
        lines.extend(make_class(name, t_def))
        lines.extend(make_end_property(parent_cls))
        

        fields = t_def.get("fields", [])
        if not fields:
            lines.append("\tpass")

        for f in fields:
            f_target = get_type_name(f["type"])
            is_scalar = f_target not in class_map
            config = {
                "f_name": f["name"],
                "f_doc": clean_doc(f.get("description")),
                "f_target": f_target,
                "ret_type": f_target if not is_scalar else name,
                "is_scalar": is_scalar
            }
            
            has_args = len(f.get("args", [])) > 0
            if has_args:
                lines.extend(make_method(**config))
            else:
                lines.extend(make_property(**config))
                
        lines.append("")

    lines.extend(make_querybuilder(query_root))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Generated {OUTPUT_FILE}")


def clean_doc(desc):
    if not desc: return ""
    return desc.replace('"', "'").replace('\n', ' ')


def get_type_name(t):
    while t.get("ofType"): t = t["ofType"]
    return t.get("name") or "Any"


def find_types(d):
    if isinstance(d, dict):
        if "types" in d and isinstance(d["types"], list) and d["types"]:
            return d["types"]
        for k in d:
            res = find_types(d[k])
            if res:
                return res
    return None


def first_pass(types):
    class_map = {} # name -> fields
    parent_map = {} # child -> parent
    
    for t in types:
        if t.get("kind") == "OBJECT" and not t["name"].startswith("__"):
            class_map[t["name"]] = t
            
            for f in t.get("fields", []):
                target = get_type_name(f["type"])
                if target not in parent_map:
                    parent_map[target] = t["name"]
                elif t["name"] == "CoreEntry": 
                    parent_map[target] = "CoreEntry" 

    return class_map, parent_map


def make_class(name: str, t_def: dict):
    lines = []
    lines.append(f"class {name}(QueryNode):")
    doc = clean_doc(t_def.get("description"))
    lines.append(f"\t\"\"\"{doc}\"\"\"")
    return lines


def make_end_property(parent_cls):
    """Allows move back up node"""
    lines = []
    lines.append(f"\t@property")
    lines.append(f"\tdef end(self) -> '{parent_cls}':")
    lines.append(f"\t\t\"\"\"Return to parent ({parent_cls})\"\"\"")
    lines.append(f"\t\treturn self._parent if self._parent else self")
    return lines


def make_method(f_name: str, f_doc: str, f_target: str, ret_type: str, is_scalar: str):
    """Generates a method for fields that require arguments."""
    lines = [
        f"\tdef {f_name}(self, **kwargs) -> '{ret_type}':",
        f"\t\t\"\"\"{f_doc}\"\"\""
    ]
    if is_scalar:
        lines.append(f"\t\tself._enter('{f_name}', QueryNode, **kwargs)")
        lines.append(f"\t\treturn self")
    else:
        lines.append(f"\t\treturn self._enter('{f_name}', {f_target}, **kwargs)")
    return lines


def make_property(f_name: str, f_doc: str, f_target: str, ret_type: str, is_scalar: bool) -> list:
    """Generates a property for fields without arguments."""
    f_name = f"{f_name}_" if keyword.iskeyword(f_name) else f_name # class is a property 

    lines = [
        f"\t@property",
        f"\tdef {f_name}(self) -> '{ret_type}':",
        f"\t\t\"\"\"{f_doc}\"\"\""
    ]
    if is_scalar:
        lines.append(f"\t\tself._enter('{f_name}', Query)")
        lines.append(f"\t\treturn self")
    else:
        lines.append(f"\t\treturn self._enter('{f_name}', {f_target})")
    return lines


def make_querybuilder(query_root: str) -> list:
    """Generates the main entry point function for the API."""
    return [
        f"def QueryBuilder() -> {query_root}:",
        f"\t\"\"\"Initializes a new GraphQL query builder root.\"\"\"",
        f"\treturn {query_root}(name=None)"
    ]

if __name__ == "__main__":
    make_code()
