import requests
import textwrap
from copy import deepcopy

class QueryBuilder:
    # (Methods remain the same as the previous response)
    def __init__(self, name=None, parent=None):
        self.name = name
        self.parent = parent
        self.children = []

    def clone(self):
        return deepcopy(self)

    def add(self, *fields):
        for f in fields:
            self.children.append(f)
        return self

    def enter(self, field_name):
        node = QueryBuilder(field_name, parent=self)
        self.children.append(node)
        return node

    def raw(self, gql: str):
        clean = textwrap.dedent(gql).strip()
        self.children.append(clean)
        return self

    def end(self):
        # For general nodes, this returns the parent node
        return self.parent

    def _render_node(self, indent=0):
        pad = " " * indent

        # --- ROOT NODE RENDERING (self.name is None) ---
        if self.name is None:
            parts = []
            for c in self.children:
                if isinstance(c, QueryBuilder):
                    # FIX 1: When rendering a child node from the root,
                    # we should start its rendering at the current indent level.
                    parts.append(c._render_node(indent))
                else:
                    # Scalar or raw block: split and apply the current indent
                    lines = c.split("\n")
                    # FIX 2: Apply the pad to each line, then join
                    lines = [pad + line for line in lines]
                    parts.append("\n".join(lines))
            return "\n".join(parts).rstrip()

        # --- NESTED NODE RENDERING ---
        inner_lines = []
        for c in self.children:
            if isinstance(c, QueryBuilder):
                # Nested node: increase indent by 2
                inner_lines.append(c._render_node(indent + 2))
            else:
                # Scalar or raw block: split and apply the increased indent
                lines = c.split("\n")
                # FIX 3: Apply indent + 2 pad to each line, then join
                lines = [(" " * (indent + 2)) + line for line in lines]
                inner_lines.append("\n".join(lines))

        inner = "\n".join(inner_lines)
        return f"{pad}{self.name} {{\n{inner}\n{pad}}}"

    def render(self):
        fields = self._render_node(indent=4)
        query = f"""
query structure($id: String!) {{
entry(entry_id: $id) {{
{fields}
}}
}}"""
        return textwrap.dedent(query).strip()

def submit_query(query, entry_id: str):
    response = requests.post(
        "https://data.rcsb.org/graphql",
        json={"query": query, "variables": {"id": entry_id}},
    ).json()
    entry_data = response["data"]["entry"]
    return entry_data

if __name__ == "__main__":
    QB = QueryBuilder()
    
    builder = (
        QB.clone()
        .enter("polymer_entities")
            .raw("""
             rcsb_target_cofactors {
                 cofactor_SMILES
             }
             """)
            .enter("rcsb_polymer_entity_annotation")
                .add("annotation_id", "type")
            .end()

            .raw("rcsb_id")
            .raw("annotation_type")
        .end() # Back to Root
        
    )
    print(type(builder))

    query = builder.render()
    print(query)

    raw_entry = submit_query(query, "1b38")
    print(raw_entry)
