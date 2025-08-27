import json
from copy import deepcopy
from typing import Dict, Set, Any, Union, Optional

import jsonschema
import yaml

# Schema for validating templates themselves
TEMPLATE_META_SCHEMA = {
    "type": "object",
    "required": ["config_schema", "server_name", "command", "args", "env"],
    "properties": {
        "config_schema": {
            "type": "object",
            "required": ["type", "properties"],
            "properties": {
                "type": {"const": "object"},
                "required": {"type": "array", "items": {"type": "string"}},
                "properties": {"type": "object"}
            }
        },
        "server_name": {"type": "string"},
        "command": {
            "type": "string",
            "enum": ["npx", "uvx"]
        },
        "args": {"type": "array"},
        "env": {"type": "array"},
        "license": {"type": "string"},
        "description": {"type": "string"},
        "owner": {"type": "string"},
        "package": {"type": "string"},
        "vendor": {"type": "string"},
    }
}


class ConfigProcessor:
    """
    A class to process configuration templates from YAML strings and handle user configurations in JSON.

    This processor accepts YAML input strings for templates, but expects JSON for user configurations.
    All validation, processing, and substitution are done with JSON-compatible objects (dicts) internally.
    Output can be formatted as either YAML or JSON.
    """

    def validate_template(self, template_yaml: str) -> Dict[str, Any]:
        """
        Validate a template YAML string.

        Args:
            template_yaml: YAML string containing the template

        Returns:
            The parsed and validated template as a dict (JSON-compatible object)

        Raises:
            TypeError: If the input is not a string
            ValueError: If the template is invalid YAML or doesn't match the schema
        """
        if not isinstance(template_yaml, str):
            raise TypeError("Template must be a YAML string")

        try:
            # Parse the template YAML to a JSON-compatible dict
            template = yaml.safe_load(template_yaml)

            # Validate against the meta-schema
            jsonschema.validate(instance=template, schema=TEMPLATE_META_SCHEMA)

            # Validate config references
            self._validate_config_references(template)

            # Return the template as a dict (JSON-compatible object)
            return template
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}")
        except jsonschema.exceptions.ValidationError as e:
            raise ValueError(f"Invalid template structure: {e}")

    def _validate_config_references(self, template: Dict[str, Any]) -> None:
        """
        Validate that all config references point to properties in the configSchema.

        Args:
            template: The template to validate

        Raises:
            ValueError: If a reference is invalid
        """
        # Get all defined properties in configSchema
        schema_properties = set(template.get("config_schema", {}).get("properties", {}).keys())

        # Find all config references in the template
        references = self._find_config_references(template)

        # Check each reference
        for ref in references:
            # Extract property name after "config."
            prop = ref[7:]  # Remove "config." prefix

            # Handle camelCase to snake_case conversion
            if prop == "userId":
                prop = "user_id"

            # Verify the property exists in the schema
            if prop not in schema_properties:
                raise ValueError(f"Config reference '{ref}' does not match any property in config_schema")

    def _find_config_references(self, obj: Any, refs: Optional[Set[str]] = None) -> Set[str]:
        """
        Recursively find all strings that look like config references.

        Args:
            obj: The object to search
            refs: Set to collect references

        Returns:
            Set of config references
        """
        if refs is None:
            refs = set()

        if isinstance(obj, str) and obj.startswith("config."):
            refs.add(obj)
        elif isinstance(obj, list):
            for item in obj:
                self._find_config_references(item, refs)
        elif isinstance(obj, dict):
            for key, value in obj.items():
                # Skip the configSchema itself
                if key != "config_schema":
                    self._find_config_references(value, refs)

        return refs

    def validate_user_config(self,
                             template: Dict[str, Any],
                             user_config_json: Union[str, Dict[str, Any]]
                             ) -> Dict[str, Any]:
        """
        Validate user configuration against the template's configSchema.

        Args:
            template: The template containing configSchema
            user_config_json: JSON string or dict with user-provided configuration

        Returns:
            The parsed and validated user config as a dict (JSON-compatible object)

        Raises:
            ValueError: If the configuration is invalid
            TypeError: If the input cannot be parsed as JSON
        """
        if "config_schema" not in template:
            raise ValueError("Template does not contain a config_schema")

        try:
            # Parse the user config if it's a JSON string
            if isinstance(user_config_json, str):
                try:
                    user_config = json.loads(user_config_json)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON in user configuration: {e}")
            else:
                # Already a dict or similar object
                user_config = user_config_json

            # Validate against the schema
            jsonschema.validate(instance=user_config, schema=template["config_schema"])

            # Return as dict (JSON-compatible object)
            return user_config
        except jsonschema.exceptions.ValidationError as e:
            raise ValueError(f"Invalid user configuration: {e}")

    def process_configuration(self,
                              template: Dict[str, Any],
                              user_config: Union[str, Dict[str, Any]]
                              ) -> Dict[str, Any]:
        """
        Process a template with user configuration.

        Args:
            template: The template to process
            user_config: User-provided configuration as dict or JSON string

        Returns:
            Processed configuration with references substituted (JSON-compatible object)

        Raises:
            ValueError: If user_config is invalid JSON
            TypeError: If user_config is not a dict or cannot be parsed to a dict
        """
        # Parse user config if it's a JSON string
        if isinstance(user_config, str):
            try:
                user_config = json.loads(user_config)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in user configuration: {e}")

        # Ensure user_config is a dict (JSON object)
        if not isinstance(user_config, dict):
            raise TypeError("User configuration must be a dict or a JSON string that parses to a dict")

        # Deep copy to avoid modifying the original
        result = deepcopy(template)

        # Replace configSchema with actual config
        if "config_schema" in result:
            del result["config_schema"]
        result["config"] = user_config

        # Process all template values to substitute config references
        def substitute_refs(value):
            if isinstance(value, str) and value.startswith("config."):
                prop = value[7:]  # Remove "config." prefix

                # Handle camelCase to snake_case conversion
                if prop == "userId":
                    prop = "user_id"

                if prop in user_config:
                    return user_config[prop]
                return ""

            elif isinstance(value, dict) and "env" in value:
                env_vars = value["env"]
                if isinstance(env_vars, list):
                    return {var["name"]: var["value"] for var in env_vars if "name" in var and "value" in var}
                return value

            elif isinstance(value, list):
                return [substitute_refs(item) for item in value]

            elif isinstance(value, dict):
                return {k: substitute_refs(v) for k, v in value.items()}

            return value

        # Process all values except the config itself
        for key in result:
            if key != "config":
                result[key] = substitute_refs(result[key])

        return result

    def get_schema(self, template_yaml: str) -> Dict[str, Any]:
        """
        Extract the schema from a template.

        Args:
            template_yaml: YAML string containing the template

        Returns:
            The extracted schema

        Raises:
            ValueError: If the template is invalid or doesn't contain a configSchema
            TypeError: If template_yaml is not a string
        """
        template = self.validate_template(template_yaml)
        schema = template.get("config_schema")

        if not schema:
            raise ValueError("Template does not contain a config_schema")

        return schema

    def output_yaml(self, data: Dict[str, Any]) -> str:
        """
        Convert data to a YAML string.

        Args:
            data: The data to convert

        Returns:
            YAML representation of the data
        """
        return yaml.dump(data, default_flow_style=False, sort_keys=False)

    def output_json(self, data: Dict[str, Any]) -> str:
        """
        Convert data to a JSON string.

        Args:
            data: The data to convert

        Returns:
            JSON representation of the data
        """
        return json.dumps(data, indent=2)
