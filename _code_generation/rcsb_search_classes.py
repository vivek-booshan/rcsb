import json
import os
import sys

# Configuration
INPUT_FILE = "resources/structure_schema.json"
OUTPUT_FILE = "search.py"

# --- STATIC HEADER ---
HEADER = """# This file is auto-generated. Do not edit directly.
from typing import Any, List, Union, Dict, Optional, Literal

# --- Node Architecture ---
class SearchNode:
    \"\"\"Base class for all RCSB Search API nodes.\"\"\"
    def __and__(self, other: 'SearchNode') -> 'GroupNode':
        return GroupNode("and", [self, other])

    def __or__(self, other: 'SearchNode') -> 'GroupNode':
        return GroupNode("or", [self, other])

    def to_dict(self) -> dict:
        raise NotImplementedError

class GroupNode(SearchNode):
    def __init__(self, operator: str, nodes: List[SearchNode]):
        self.operator = operator
        self.nodes = []
        for node in nodes:
            if isinstance(node, GroupNode) and node.operator == operator:
                self.nodes.extend(node.nodes)
            else:
                self.nodes.append(node)

    def to_dict(self) -> dict:
        return {
            "type": "group",
            "logical_operator": self.operator,
            "nodes": [node.to_dict() for node in self.nodes]
        }

class TerminalNode(SearchNode):
    def __init__(self, service: str, parameters: dict, label: str = None):
        self.service = service
        self.parameters = parameters
        self.label = label

    def to_dict(self) -> dict:
        node = {"type": "terminal", "service": self.service, "parameters": self.parameters}
        if self.label:
            node["label"] = self.label
        return node

    def equals(self, val: Any) -> TerminalNode: return self._op("exact_match", val)
    def contains(self, val: str) -> TerminalNode: return self._op("contains_phrase", val)
    def contains_words(self, val: str) -> TerminalNode: return self._op("contains_words", val)
    def greater_than(self, val: Union[int, float]) -> TerminalNode: return self._op("greater", val)
    def greater_or_equal(self, val: Union[int, float]) -> TerminalNode: return self._op("greater_or_equal", val)
    def less_than(self, val: Union[int, float]) -> TerminalNode: return self._op("less", val)
    def less_or_equal(self, val: Union[int, float]) -> TerminalNode: return self._op("less_or_equal", val)
    def range(self, min_val: Any, max_val: Any) -> TerminalNode: return self._op("range", [min_val, max_val])
    def in_set(self, val_list: List[Any]) -> TerminalNode: return self._op("in", val_list)
    def exists(self) -> TerminalNode: return self._op("exists")

# --- Service Helper Functions ---

def FullTextQuery(value: str) -> TerminalNode:
    \"\"\"
    Global keyword search across all indexed text fields.
    Example: FullTextQuery("aspirin")
    \"\"\"
    return TerminalNode("full_text", {"value": value})

def SequenceQuery(value: str, sequence_type: Literal["protein", "dna", "rna"] = "protein", 
                 identity_cutoff: float = 0.9, evalue_cutoff: float = 0.1) -> TerminalNode:
    \"\"\"
    Sequence similarity search (BLAST-like).
    Args:
        value: The sequence string (one letter code).
        sequence_type: 'protein', 'dna', or 'rna'.
        identity_cutoff: Minimum identity (0.0 - 1.0).
        evalue_cutoff: Maximum E-value.
    \"\"\"
    return TerminalNode("sequence", {
        "value": value, "sequence_type": sequence_type,
        "identity_cutoff": identity_cutoff, "evalue_cutoff": evalue_cutoff
    })

def MotifQuery(value: str, pattern_type: Literal["simple", "prosite", "regex"] = "simple") -> TerminalNode:
    \"\"\"
    Sequence motif search.
    Args:
        value: Pattern string (e.g. 'C-x(2,4)-C').
        pattern_type: 'simple', 'prosite', or 'regex'.
    \"\"\"
    return TerminalNode("seqmotif", {"value": value, "pattern_type": pattern_type})

def StructureMotifQuery(entry_id: str, residue_ids: List[dict], assembly_id: str = "1") -> TerminalNode:
    \"\"\"
    3D Structure motif search (substructure similarity).
    Args:
        entry_id: PDB ID of the reference structure (e.g., '1MCT').
        residue_ids: List of residues defining the active site/motif.
                     e.g. [{'chain_id': 'A', 'struct_oper_id': '1', 'label_seq_id': 57}]
    \"\"\"
    return TerminalNode("structure", {
        "value": {
            "entry_id": entry_id,
            "assembly_id": assembly_id,
            "residue_ids": residue_ids
        },
        "operator": "strict_shape_match" # Default operator
    })

def ChemicalQuery(value: str, type: Literal["formula", "descriptor"] = "formula", 
                 match_type: Literal["graph-exact", "graph-relaxed", "fingerprint-similarity", "sub-struct-graph-exact"] = None) -> TerminalNode:
    \"\"\"
    Chemical formula or structure search (SMILES/InChI).
    Args:
        value: The formula (e.g., 'C8 H10 N4 O2') or descriptor string.
        type: 'formula' or 'descriptor'.
        match_type: Required if type='descriptor'. e.g. 'graph-exact', 'fingerprint-similarity'.
    \"\"\"
    params = {"value": value, "type": type}
    if match_type:
        params["match_type"] = match_type
    return TerminalNode("chemical", params)

# --- Request Builder ---
class SearchRequest:
    \"\"\"Wrapper to construct the final JSON payload for the Search API.\"\"\"
    def __init__(self, query: SearchNode, return_type: ReturnType = "entry"):
        self.query = query
        self.return_type = return_type
        self.options = {}

    def paginate(self, start: int, rows: int):
        self.options["paginate"] = {"start": start, "rows": rows}
        return self

    def sort(self, field: str = "score", direction: Literal["asc", "desc"] = "desc"):
        if "sort" not in self.options: self.options["sort"] = []
        self.options["sort"].append({"sort_by": field, "direction": direction})
        return self

    def to_dict(self) -> dict:
        payload = {
            "query": self.query.to_dict(),
            "return_type": self.return_type
        }
        if self.options:
            payload["request_options"] = self.options
        return payload

# --- Generated Classes ---
"""


def get_class_name(path):
    if not path: return "AttributesRoot"
    return "Attr_" + ''.join(p.capitalize() for p in path.split('.')[-1].split('_'))

def clean_doc(s):
    if not s: return ""
    # Escape triple quotes to prevent syntax errors in the generated python file
    return s.replace('"', "'").replace('\\', '/').replace('\n', ' ').strip()

def run_generator():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    print("Loading schema...")
    with open(INPUT_FILE, "r", encoding='utf-8') as f:
        schema = json.load(f)

    generated_code = []
    seen_classes = {}

    def walk(node, path=""):
        # Merge properties from current node and branches
        props = node.get("properties", {}).copy()
        
        if node.get("type") == "array" and "items" in node:
            props.update(node["items"].get("properties", {}))
            
        for branch in ["oneOf", "anyOf", "allOf"]:
            if branch in node:
                for option in node[branch]:
                    props.update(option.get("properties", {}))

        if not props:
            return None

        # Class Generation
        raw_name = get_class_name(path)
        cls_name = f"{raw_name}_{abs(hash(path))}"
        
        if path in seen_classes:
            return seen_classes[path]

        lines = [f"class {cls_name}:"]
        lines.append(f"    \"\"\"{clean_doc(node.get('description', ''))}\"\"\"")

        for key, val in props.items():
            full_path = f"{path}.{key}" if path else key
            
            # Heuristic: Object vs Attribute
            is_obj = False
            if val.get("type") == "object": is_obj = True
            elif val.get("type") == "array" and val.get("items", {}).get("type") == "object": is_obj = True
            elif val.get("properties") or any(b in val for b in ["oneOf", "anyOf", "allOf"]): is_obj = True

            doc = clean_doc(val.get("description", ""))

            if is_obj:
                child_cls = walk(val, full_path)
                if child_cls:
                    # FIX 1: Explicit indentation (8 spaces) for docstring and return
                    lines.append(f"    @property")
                    lines.append(f"    def {key}(self) -> '{child_cls}':")
                    lines.append(f"        \"\"\"{doc}\"\"\"")
                    lines.append(f"        return {child_cls}()")
            else:
                # FIX 2: Move docstring INTO the function body, not the Attribute constructor
                lines.append(f"    @property")
                lines.append(f"    def {key}(self) -> Attribute:")
                lines.append(f"        \"\"\"{doc}\"\"\"")
                lines.append(f"        return Attribute('{full_path}')")

        generated_code.append("\n".join(lines))
        seen_classes[path] = cls_name
        return cls_name

    print("Traversing schema tree...")
    root_cls = walk(schema)

    print(f"Writing {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
        f.write(HEADER + "\n")
        f.write("\n\n".join(generated_code) + "\n\n")
        f.write(f"attrs = {root_cls}()\n")
    
    print("Done!")

if __name__ == "__main__":
    run_generator()
