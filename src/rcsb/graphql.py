from __future__ import annotations
from typing import Any, List, Dict, Optional, Union, Self, Type
import textwrap
from copy import deepcopy
from rcsb.schema import _INTERNAL_SCHEMA
import requests

class QueryBuilder:
    def __init__(self, name: Optional[str] = None, parent: Optional[QueryBuilder] = None, schema_type: Optional[str] = None):
        self.name = name
        self.parent = parent
        self.children: List[Union[QueryBuilder, str]] = []
        self.arguments: Dict[str, Any] = {}
        # Default to root schema type
        self.schema_type = schema_type or _INTERNAL_SCHEMA.query_type

    def __call__(self, **kwargs) -> Self:
        """Adds arguments and returns self, maintaining the 'Proxy' type."""
        self.arguments.update(kwargs)
        return self

    def __getattr__(self, name):
        if name.startswith('_'): raise AttributeError(name)

        field_def, target_type = _INTERNAL_SCHEMA.get_field(self.schema_type, name)
        
        if field_def:
            target_def = _INTERNAL_SCHEMA.types.get(target_type, {})
            # --- THE FIX ---
            # We return the node/field WITHOUT adding it to self.children yet.
            # We only add it when we know for sure it's part of the query.
            return self._create_temporary_node(name, target_type, target_def)
        
        raise AttributeError(f"'{self.schema_type}' has no attribute '{name}'")

    def _create_temporary_node(self, name, target_type, target_def):
        """Creates a node that only attaches itself to the parent when used."""
        is_scalar = target_def.get("kind") in ("SCALAR", "ENUM")
        
        if is_scalar:
            # For scalars, we add them immediately because the dot access IS the selection
            if name not in self.children:
                self.children.append(name)
            return self 
        else:
            # For objects, we create the node but don't append to self.children 
            # until the user actually does something with it.
            new_node = QueryBuilder(name, parent=self, schema_type=target_type)
            self.children.append(new_node)
            return new_node

    def __dir__(self) -> List[str]:
        # Merges standard methods with schema-specific fields
        return list(super().__dir__()) + _INTERNAL_SCHEMA.list_fields(self.schema_type)

    def _ipython_key_completions_(self):
        """Specific hook for Jupyter/IPython to force-refresh field lists."""
        return _INTERNAL_SCHEMA.list_fields(self.schema_type)

    def enter(self, field_name: str, schema_type: Optional[str] = None) -> QueryBuilder:
        node = QueryBuilder(field_name, parent=self, schema_type=schema_type)
        self.children.append(node)
        return node

    def add(self, *fields: str) -> Self:
        for f in fields:
            if f not in self.children: self.children.append(f)
        return self

    def raw(self, gql: str) -> Self:
        """Add a raw GraphQL string block to the current node."""
        clean = textwrap.dedent(gql).strip()
        self.children.append(clean)
        return self

    @property
    def end(self) -> Self:
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
        root = self
        while root.parent is not None:
            root = root.parent

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

class SchemaProxy:
    """
    A transparent wrapper around QueryBuilder that tricks IDEs into 
    treating different schema nodes as different 'types' for completion.
    """
    @classmethod
    def create(cls, builder_instance: QueryBuilder) -> Any:
        # Create a dynamic subclass so the IDE treats each level uniquely
        class_name = f"QB_{builder_instance.schema_type}"
        dynamic_type = type(class_name, (QueryBuilder,), {})
        
        # Manually wrap the instance into this new dynamic type
        builder_instance.__class__ = dynamic_type
        return builder_instance
