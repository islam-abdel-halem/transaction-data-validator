"""Unit tests for data validator module."""

from src.data_validator import validate_transaction, clean_and_structure, calculate_total_sales

def test_validate_transaction():
    # Valid transaction
    assert validate_transaction("ID-1234, 150.50, US, 2023-10-01") is True
    # Invalid amount
    assert validate_transaction("ID-1235, invalid, US, 2023-10-01") is False
    # Missing field
    assert validate_transaction("ID-1236, 100, US") is False
    # Empty field
    assert validate_transaction("ID-1237, 100, , 2023-10-01") is False

def test_clean_and_structure():
    raw = [
        "ID-001, 100.0, US, 2023-01-01",
        "ID-002, bad, UK, 2023-01-02"
    ]
    cleaned = clean_and_structure(raw)
    assert len(cleaned) == 1
    assert cleaned[0] == ("ID-001", 100.0, "US", "2023-01-01")

def test_calculate_total_sales():
    structured = [
        ("ID-001", 100.0, "US", "2023-01-01"),
        ("ID-002", 50.5, "UK", "2023-01-02")
    ]
    total = calculate_total_sales(structured)
    assert total == 150.5
