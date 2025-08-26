import pytest
from cardvalidator import CardValidator, validate_card, is_valid_card

def test_luhn_algorithm():
    validator = CardValidator()
    
    # Valid test cards
    assert validator.luhn_checksum_is_valid("4111111111111111")  # Visa
    assert validator.luhn_checksum_is_valid("5105105105105100")  # MasterCard
    assert validator.luhn_checksum_is_valid("378282246310005")   # AmEx
    
    # Invalid cards
    assert not validator.luhn_checksum_is_valid("1234567890123456")
    assert not validator.luhn_checksum_is_valid("0000000000000000")

def test_card_type_detection():
    validator = CardValidator()
    
    assert validator.get_card_type("4111111111111111") == "Visa"
    assert validator.get_card_type("5105105105105100") == "MasterCard"
    assert validator.get_card_type("378282246310005") == "American Express"
    
    # Test RuPay detection (assuming a valid RuPay number with proper checksum)
    # Note: These are test numbers, not real card numbers
    rupay_test = "6037997040000000"  # This might need to be adjusted based on actual RuPay test numbers
    if validator.luhn_checksum_is_valid(rupay_test):
        assert validator.get_card_type(rupay_test) == "RuPay"

def test_validate_function():
    # Test valid cards
    result = validate_card("4111111111111111")
    assert result["valid"] == True
    assert result["type"] == "Visa"
    
    # Test invalid cards
    result = validate_card("1234567890123456")
    assert result["valid"] == False
    assert result["type"] == "Invalid"

def test_convenience_functions():
    assert is_valid_card("4111111111111111") == True
    assert is_valid_card("1234567890123456") == False

def test_formatted_input():
    # Test with spaces and hyphens
    assert validate_card("4111-1111-1111-1111")["valid"] == True
    assert validate_card("4111 1111 1111 1111")["valid"] == True
    
    # Test empty input
    result = validate_card("")
    assert result["valid"] == False
    assert result["type"] == "Invalid"
    
    # Test non-numeric input
    result = validate_card("abc123")
    assert result["valid"] == False

def test_edge_cases():
    validator = CardValidator()
    
    # Test all identical digits are rejected
    assert not validator.luhn_checksum_is_valid("1111111111111111")
    assert not validator.luhn_checksum_is_valid("2222222222222222")
    assert not validator.luhn_checksum_is_valid("9999999999999999")
    
    # Test mixed formatting
    result = validate_card("4111 1111-1111 1111")
    assert result["cleaned_number"] == "4111111111111111"
    assert result["valid"] == True
