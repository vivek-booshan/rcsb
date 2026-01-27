import json
import os
import sys

INPUT_FILE = "resources/structure_schema.json"
HEADER_FILE = "_code_generation/search_header.py"
OUTPUT_FILE = "src/rcsb/search.py"


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

    with open(HEADER_FILE, 'r') as header:
        generated_code = [header.read()]

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
                    lines.append(f"    @property")
                    lines.append(f"    def {key}(self) -> '{child_cls}':")
                    lines.append(f"        \"\"\"{doc}\"\"\"")
                    lines.append(f"        return {child_cls}()")
            else:
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
        f.write("\n\n".join(generated_code) + "\n\n")
        f.write(f"attrs = {root_cls}()\n")
    
    print("Done!")

if __name__ == "__main__":
    run_generator()
