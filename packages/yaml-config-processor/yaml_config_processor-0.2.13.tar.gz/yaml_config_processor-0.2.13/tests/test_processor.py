import json
import os
import pytest
from yaml_config_processor import ConfigProcessor


# Fixture paths
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')
TEMPLATE_PATH = os.path.join(FIXTURES_DIR, 'example_template.yaml')
CONFIG_PATH = os.path.join(FIXTURES_DIR, 'example_config.json')


@pytest.fixture
def processor():
    """Create a ConfigProcessor instance for testing."""
    return ConfigProcessor()


@pytest.fixture
def template_yaml():
    """Load example template YAML for testing."""
    with open(TEMPLATE_PATH, 'r') as f:
        return f.read()


@pytest.fixture
def config_json():
    """Load example config JSON for testing."""
    with open(CONFIG_PATH, 'r') as f:
        return f.read()


class TestConfigProcessor:
    """Tests for the ConfigProcessor class."""

    def test_validate_template(self, processor, template_yaml):
        """Test template validation."""
        # Valid template should parse correctly
        template = processor.validate_template(template_yaml)
        assert isinstance(template, dict)
        assert "configSchema" in template
        assert "service_name" in template
        assert template["service_name"] == "example-service"

        # Invalid template should raise ValueError
        with pytest.raises(ValueError):
            processor.validate_template("invalid: - yaml: content")

        # Non-string input should raise TypeError
        with pytest.raises(TypeError):
            processor.validate_template(123)

    def test_get_schema(self, processor, template_yaml):
        """Test schema extraction."""
        schema = processor.get_schema(template_yaml)
        assert isinstance(schema, dict)
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "api_key" in schema["properties"]

    def test_validate_user_config(self, processor, template_yaml, config_json):
        """Test user config validation."""
        template = processor.validate_template(template_yaml)

        # Valid config should pass validation
        user_config = processor.validate_user_config(template, config_json)
        assert isinstance(user_config, dict)
        assert user_config["api_key"] == "abc123xyz456"

        # Config dict should also work
        config_dict = json.loads(config_json)
        user_config = processor.validate_user_config(template, config_dict)
        assert isinstance(user_config, dict)

        # Invalid JSON should raise ValueError
        with pytest.raises(ValueError):
            processor.validate_user_config(template, "{invalid json")

        # Missing required field should raise ValueError
        invalid_config = {"api_key": "test"}  # missing user_id and base_url
        with pytest.raises(ValueError):
            processor.validate_user_config(template, invalid_config)

    def test_process_configuration(self, processor, template_yaml, config_json):
        """Test configuration processing."""
        template = processor.validate_template(template_yaml)
        user_config = processor.validate_user_config(template, config_json)

        # Process the configuration
        processed = processor.process_configuration(template, user_config)

        # Check that references were substituted
        assert processed["user_id"] == "user1"  # config.userId -> user_id
        assert processed["args"][2] == "https://api.example.com"  # config.base_url
        assert processed["env"][0]["value"] == "abc123xyz456"  # config.api_key

        # Check that config is included
        assert "config" in processed
        assert processed["config"] == user_config

        # Check that configSchema is removed
        assert "configSchema" not in processed

    def test_output_formats(self, processor, template_yaml, config_json):
        """Test output formatting."""
        template = processor.validate_template(template_yaml)
        user_config = processor.validate_user_config(template, config_json)
        processed = processor.process_configuration(template, user_config)

        # YAML output
        yaml_output = processor.output_yaml(processed)
        assert isinstance(yaml_output, str)
        assert "service_name: example-service" in yaml_output

        # JSON output
        json_output = processor.output_json(processed)
        assert isinstance(json_output, str)
        assert '"service_name": "example-service"' in json_output
