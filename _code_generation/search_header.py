# NOTE: This file is auto-generated. Do not edit directly.
from typing import Any, List, Union, Dict, Optional, Literal

class SearchNode:
    """Base class for all RCSB Search API nodes."""
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

    def equals(self, val: Any): return self._op("exact_match", val)
    def contains(self, val: str): return self._op("contains_phrase", val)
    def contains_words(self, val: str): return self._op("contains_words", val)
    def greater_than(self, val: Union[int, float]): return self._op("greater", val)
    def greater_or_equal(self, val: Union[int, float]): return self._op("greater_or_equal", val)
    def less_than(self, val: Union[int, float]): return self._op("less", val)
    def less_or_equal(self, val: Union[int, float]): return self._op("less_or_equal", val)
    def range(self, min_val: Any, max_val: Any): return self._op("range", [min_val, max_val])
    def in_set(self, val_list: List[Any]): return self._op("in", val_list)
    def exists(self): return self._op("exists")

def FullTextQuery(value: str) -> TerminalNode:
    """
    Global keyword search across all indexed text fields.
    Example: FullTextQuery("aspirin")
    """
    return TerminalNode("full_text", {"value": value})

def SequenceQuery(value: str, sequence_type: Literal["protein", "dna", "rna"] = "protein", 
                 identity_cutoff: float = 0.9, evalue_cutoff: float = 0.1) -> TerminalNode:
    """
    Sequence similarity search (BLAST-like).
    Args:
        value: The sequence string (one letter code).
        sequence_type: 'protein', 'dna', or 'rna'.
        identity_cutoff: Minimum identity (0.0 - 1.0).
        evalue_cutoff: Maximum E-value.
    """
    return TerminalNode("sequence", {
        "value": value, "sequence_type": sequence_type,
        "identity_cutoff": identity_cutoff, "evalue_cutoff": evalue_cutoff
    })

def MotifQuery(value: str, pattern_type: Literal["simple", "prosite", "regex"] = "simple") -> TerminalNode:
    """
    Sequence motif search.
    Args:
        value: Pattern string (e.g. 'C-x(2,4)-C').
        pattern_type: 'simple', 'prosite', or 'regex'.
    """
    return TerminalNode("seqmotif", {"value": value, "pattern_type": pattern_type})

def StructureMotifQuery(entry_id: str, residue_ids: List[dict], assembly_id: str = "1") -> TerminalNode:
    """
    3D Structure motif search (substructure similarity).
    Args:
        entry_id: PDB ID of the reference structure (e.g., '1MCT').
        residue_ids: List of residues defining the active site/motif.
                     e.g. [{'chain_id': 'A', 'struct_oper_id': '1', 'label_seq_id': 57}]
    """
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
    """
    Chemical formula or structure search (SMILES/InChI).
    Args:
        value: The formula (e.g., 'C8 H10 N4 O2') or descriptor string.
        type: 'formula' or 'descriptor'.
        match_type: Required if type='descriptor'. e.g. 'graph-exact', 'fingerprint-similarity'.
    """
    params = {"value": value, "type": type}
    if match_type:
        params["match_type"] = match_type
    return TerminalNode("chemical", params)

class SearchRequest:
    """Wrapper to construct the final JSON payload for the Search API."""
    def __init__(self, query: SearchNode, return_type = "entry"):
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

