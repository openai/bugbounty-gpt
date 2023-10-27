import pytest
import bugbounty_gpt.env as env

def test_sanitize_category():
    assert env.sanitize_category("Functional Bugs or Glitches") == "FUNCTIONAL_BUGS_OR_GLITCHES"
    assert env.sanitize_category(" 123 Category with Special!@#$%^&*()") == "_123_CATEGORY_WITH_SPECIAL__________"

def test_sanitize_categories():
    categories = ["Functional Bugs", "Customer Support", "Out of Scope"]
    sanitized = env.sanitize_categories(categories)
    assert sanitized == ["FUNCTIONAL_BUGS", "CUSTOMER_SUPPORT", "OUT_OF_SCOPE"]

def test_validate_valid_categories():
    valid_config = {"categories": {"valid": ["Functional Bugs", "Customer Support"]}}
    env.validate_valid_categories(valid_config)  # Should not raise an exception

    invalid_config = {"categories": {}}
    with pytest.raises(ValueError):
        env.validate_valid_categories(invalid_config)

def test_validate_response_categories_subset():
    valid_config = {"categories": {"valid": ["Functional Bugs", "Customer Support"], "response": [{"name": "Functional Bugs"}, {"name": "Customer Support"}]}}
    env.validate_response_categories_subset(valid_config)  # Should not raise an exception

    invalid_config = {"categories": {"valid": ["Functional Bugs"], "response": [{"name": "Customer Support"}]}}
    with pytest.raises(ValueError):
        env.validate_response_categories_subset(invalid_config)

def test_validate_response_pairs():
    valid_config = {"categories": {"response": [{"name": "Functional Bugs", "response": "Response Text"}]}}
    env.validate_response_pairs(valid_config)  # Should not raise an exception

    invalid_config_name_missing = {"categories": {"response": [{"response": "Response Text"}]}}
    with pytest.raises(ValueError):
        env.validate_response_pairs(invalid_config_name_missing)

    invalid_config_response_missing = {"categories": {"response": [{"name": "Functional Bugs"}]}}
    with pytest.raises(ValueError):
        env.validate_response_pairs(invalid_config_response_missing)
