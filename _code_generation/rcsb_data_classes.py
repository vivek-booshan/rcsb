import json
import re
import keyword
import pathlib

INPUT_FILE = "resources/data_api_schema.json"
OUTPUT_FILE = "src/rcsb/data.py"

HEADER_FILE = "_code_generation/data_header.py"

def make_code():
    with open(INPUT_FILE, "r") as f:
        data = json.load(f)

    types = find_types(data)
    if not types:
        raise ValueError("Error: No types found in JSON.")

    class_map, parent_map = first_pass(types)

    with open(HEADER_FILE, 'r') as f:
        lines = [f.read()]
    
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
