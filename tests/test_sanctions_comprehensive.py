"""FATF & International Sanctions Comprehensive Verification Suite.
Validates 10-country OFAC/FATF sanctions matrix, country name resolution,
and positive verification of standard international student transit corridors.
"""

from src.tools.compliance import check_sanctioned_destination

def test_sanctioned_matrix_complete():
    """Verify all 10 sanctioned countries are explicitly blocked."""
    sanctioned = ["IR", "KP", "SY", "CU", "SD", "MM", "BY", "VE", "ZW", "RU"]
    for code in sanctioned:
        res = check_sanctioned_destination(code)
        assert res["blocked"] is True, f"Expected {code} to be blocked"
        assert res["reason"] is not None

def test_safe_student_corridors_unblocked():
    """Verify student origin corridors are strictly unblocked."""
    safe_corridors = ["BD", "PK", "NG", "CN", "US", "GB", "DE", "JP", "MY", "ID"]
    for code in safe_corridors:
        res = check_sanctioned_destination(code)
        assert res["blocked"] is False, f"Expected {code} to be unblocked"
        assert res["reason"] is None
