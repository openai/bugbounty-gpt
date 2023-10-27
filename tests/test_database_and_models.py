import src.db.models as models

def test_sanitize_category_name():
    assert models._sanitize_category_name("Test Category") == "TEST_CATEGORY"

def test_create_enum_members():
    categories = ["Category One", "Category Two"]
    expected_members = {"CATEGORY_ONE": "Category One", "CATEGORY_TWO": "Category Two"}
    assert models._create_enum_members(categories) == expected_members

def test_report_category_enum():
    assert models.ReportCategory.POLICY_OR_CONTENT_COMPLAINTS.value == "POLICY_OR_CONTENT_COMPLAINTS"
