
import json
from pkgutil import get_data


class _SchemaManager:
    def __init__(self):
        try:
            raw_data = get_data("rcsb", "resources/data_api_schema.json")
            if raw_data is None:
                raise FileNotFoundError("Internal schema resource not found.")
            
            full_schema = json.loads(raw_data)
            schema_data = full_schema["data"]["__schema"]
            
            # Index types for the QueryBuilder
            self.types = {t["name"]: t for t in schema_data["types"] if t["name"]}
            self.query_type = schema_data["queryType"]["name"]
        except Exception as e:
            raise RuntimeError(f"Library Initialization Error: {e}")

    def _unwrap_type(self, type_info):
        """Recursively unwraps GraphQL types to find the base name."""
        if type_info.get("name"):
            return type_info["name"]
        return self._unwrap_type(type_info["ofType"])

    def get_field(self, type_name, field_name):
        type_def = self.types.get(type_name)
        if not type_def or "fields" not in type_def:
            return None, None
            
        for field in type_def["fields"]:
            if field["name"] == field_name:
                return field, self._unwrap_type(field["type"])
        return None, None

    def list_fields(self, type_name):
        type_def = self.types.get(type_name)
        return [f["name"] for f in type_def.get("fields", [])] if type_def else []

_INTERNAL_SCHEMA = _SchemaManager()

