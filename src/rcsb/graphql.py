import requests
import textwrap
from copy import deepcopy
from .schema import _INTERNAL_SCHEMA

class QueryBuilder:
    def __init__(self, name=None, parent=None, schema_type=None):
        """
        A recursive GraphQL query builder with RCSB schema awareness.
        
        Args:
            name: The name of the GraphQL field (e.g., 'entry', 'rcsb_id').
            parent: The parent QueryBuilder node.
            schema_type: The GraphQL type from the schema (e.g., 'CoreEntry').
                         Defaults to 'Query' (the root entry point).
        """
        self.name = name
        self.parent = parent
        self.children = []
        self.arguments = {}
        # Default to 'Query' root if no context is provided
        self.schema_type = schema_type or _INTERNAL_SCHEMA.query_type

    def clone(self):
        """Returns a deep copy of the current builder."""
        return deepcopy(self)

    def __call__(self, **kwargs):
        """Adds arguments to the current node: qb.entry(entry_id="4HHB")."""
        self.arguments.update(kwargs)
        return self

    def __getattr__(self, name):
        """
        Enables dot-notation discovery and automatic node creation.
        If a field is a scalar, it is added; if it is an object, it is entered.
        """
        field_def, target_type = _INTERNAL_SCHEMA.get_field(self.schema_type, name)
        
        if field_def:
            target_def = _INTERNAL_SCHEMA.types.get(target_type, {})
            # If the field is a leaf (Scalar or Enum), just add it to the query
            if target_def.get("kind") in ("SCALAR", "ENUM"):
                return self.add(name)
            # Otherwise, it's a nested object; enter a new QueryBuilder context
            return self.enter(name, schema_type=target_type)
        
        raise AttributeError(f"Type '{self.schema_type}' has no attribute '{name}'")

    def __dir__(self):
        """Enables tab-completion in IDEs/REPLs based on the current schema context."""
        return super().__dir__() + _INTERNAL_SCHEMA.list_fields(self.schema_type)

    def add(self, *fields):
        """Explicitly add scalar fields to the current node."""
        for f in fields:
            if f not in self.children:
                self.children.append(f)
        return self

    def enter(self, field_name, schema_type=None):
        """Explicitly enter a nested node. Useful if type cannot be inferred."""
        node = QueryBuilder(
            field_name, 
            parent=self, 
            schema_type=schema_type or _INTERNAL_SCHEMA.query_type
        )
        self.children.append(node)
        return node

    def raw(self, gql: str):
        """Add a raw GraphQL string block to the current node."""
        clean = textwrap.dedent(gql).strip()
        self.children.append(clean)
        return self

    def end(self):
        """Returns the parent node, or self if at root."""
        return self.parent if self.parent else self

    def describe(self):
        """Prints official RCSB documentation for available fields at this level."""
        fields = _INTERNAL_SCHEMA.types.get(self.schema_type, {}).get("fields", [])
        print(f"\n--- {self.schema_type} Schema Context ---")
        for f in fields:
            desc = f.get("description", "No description.").strip().split('\n')[0]
            print(f"- {f['name']}: {desc}")
        return self

    def _render_node(self, indent=0):
        pad = " " * indent
        
        # Format the field name with arguments if present
        name_part = self.name
        if self.arguments:
            args = []
            for k, v in self.arguments.items():
                val = f'"{v}"' if isinstance(v, str) and not v.startswith("$") else str(v)
                args.append(f"{k}: {val}")
            name_part = f"{self.name}({', '.join(args)})"

        # Handle leaf nodes (just strings) or the Root node (name is None)
        if self.name is None:
            parts = []
            for c in self.children:
                if isinstance(c, QueryBuilder):
                    parts.append(c._render_node(indent))
                else:
                    parts.append(pad + c)
            return "\n".join(parts).rstrip()

        # Handle nested nodes
        inner_lines = []
        for c in self.children:
            if isinstance(c, QueryBuilder):
                inner_lines.append(c._render_node(indent + 2))
            else:
                inner_lines.append((" " * (indent + 2)) + c)

        inner = "\n".join(inner_lines)
        return f"{pad}{name_part} {{\n{inner}\n{pad}}}"

    def render(self, query_name="structure"):
        """Renders the full GraphQL query string."""
        fields = self._render_node(indent=2)
        return textwrap.dedent(f"""
            query {query_name} {{
            {fields}
            }}
        """).strip()


def submit_query(query, variables=None):
    """Executes a GraphQL query against the RCSB API."""
    response = requests.post(
        "https://data.rcsb.org/graphql",
        json={"query": query, "variables": variables or {}},
    ).json()
    
    if "errors" in response:
        raise RuntimeError(f"GraphQL Error: {response['errors']}")
    
    return response.get("data", {})
