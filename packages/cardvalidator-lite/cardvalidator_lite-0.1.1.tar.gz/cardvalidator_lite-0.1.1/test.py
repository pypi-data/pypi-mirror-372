from cardvalidator import validate_card, is_valid_card, CardValidator

# Quick validation
result = validate_card("4111111111111111")
print(result)
# Output: {'card_number': '4111111111111111', 'valid': True, 'type': 'Visa', 'cleaned_number': '4111111111111111'}
