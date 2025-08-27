# YAML Config Processor

A Python package for processing configuration templates from YAML strings with JSON user configurations.

## Installation

```bash
pip install yaml-config-processor
```

## Features

- Define templates in YAML for better readability
- Accept user configurations in JSON format
- Validate templates and configurations against JSON Schema
- Process templates with user configurations
- Output results in YAML or JSON format

## Usage

### Basic Example

```python
from yaml_config_processor import ConfigProcessor

# Create processor
processor = ConfigProcessor()

# Define template in YAML
template_yaml = """
configSchema:
  type: object
  required:
    - api_key
    - user_id
    - base_url
  properties:
    api_key:
      type: string
      description: API key for service
    user_id:
      type: string
      description: Unique identifier for the user
    base_url:
      type: string
      format: uri
      description: Base URL for the service
service_name: example-service
command: run
args:
  - --verbose
  - --endpoint
  - config.base_url
env:
  - name: API_KEY
    value: config.api_key
description: |
  This template defines the configuration schema and how to use the user-provided values.
  The `config.` prefix is used to reference user configuration values.
license: MIT
owner: John Doe
"""

# Define user configuration in JSON
user_config_json = """
{
    "api_key": "abc123xyz456",
    "user_id": "user1",
    "base_url": "https://api.example.com"
}
"""

# Process configuration
template = processor.validate_template(template_yaml)
user_config = processor.validate_user_config(template, user_config_json)
processed = processor.process_configuration(template, user_config)

# Output as YAML
yaml_output = processor.output_yaml(processed)
print(yaml_output)

# Output as JSON
json_output = processor.output_json(processed)
print(json_output)
```

### Step-by-Step Usage

1. **Create a template in YAML**

   Templates define both the schema for user configuration and the template structure with references to the configuration values.

2. **Validate the template**

   ```python
   template = processor.validate_template(template_yaml)
   ```

3. **Extract schema for clients (optional)**

   ```python
   schema = processor.get_schema(template_yaml)
   ```

4. **Validate user configuration**

   ```python
   user_config = processor.validate_user_config(template, user_config_json)
   ```

5. **Process configuration**

   ```python
   processed = processor.process_configuration(template, user_config)
   ```

6. **Output the result**

   ```python
   # As YAML
   yaml_result = processor.output_yaml(processed)
   
   # As JSON
   json_result = processor.output_json(processed)
   ```

## Template Format

Templates must follow this structure:

- `configSchema`: JSON Schema definition for validating user configurations
- Other fields: Template structure with references to config values

Example:

```yaml
configSchema:
  type: object
  required:
    - api_key
  properties:
    api_key:
      type: string
service_name: example-service
config_value: config.api_key
```

## Configuration References

References to configuration values use the `config.` prefix:

- `config.api_key` refers to the `api_key` property in the user config
- `config.userId` is automatically mapped to `user_id` (camelCase to snake_case)

## License

MIT License
