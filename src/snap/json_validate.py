""" Validate json Object """
import json

import jsonschema


class json_validate:
    """Load schema and validate json object"""

    def __init__(self, json_obj: object, schema_file: str):
        self.json_obj = json_obj
        self.json_schema_file = schema_file
        self.json_schema: dict = {}

        self.load_json_schemas()
        self.validate_json_obj()

    def load_json_schemas(self):
        with open(self.json_schema_file, "r") as f:
            schema_data = f.read()
        self.json_schema = json.loads(schema_data)

    def validate_json_obj(self):
        self.json_schema_result = jsonschema.validate(self.json_obj, self.json_schema)
