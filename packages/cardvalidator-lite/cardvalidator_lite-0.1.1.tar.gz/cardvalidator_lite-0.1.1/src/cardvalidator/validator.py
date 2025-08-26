class CardValidator:
    """Validator class to check credit card numbers for validity and type."""

    def __init__(self):
        # Card types with their prefix patterns and lengths
        self.card_types = {
            "Visa": {"prefixes": ["4"], "lengths": [13, 16, 19]},
            "MasterCard": {"prefixes": [str(i) for i in range(51, 56)], "lengths": [16]},
            "American Express": {"prefixes": ["34", "37"], "lengths": [15]},
            "Discover": {"prefixes": ["6011", "622126", "622925", "644", "645", "646", "647", "648", "649", "65"], "lengths": [16, 19]},
            "RuPay": {"prefixes": ["60", "65", "81"], "lengths": [16]},
        }

    def luhn_checksum_is_valid(self, card_number: str) -> bool:
        """Check if the card number is valid using the Luhn algorithm."""
        # Reject numbers with all identical digits (like 0000000000000000)
        if len(set(card_number)) == 1:
            return False
            
        def digits_of(n):
            return [int(d) for d in str(n)]

        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10 == 0

    def get_card_type(self, card_number: str) -> str:
        """Determine the card type based on prefix and length."""
        for card_type, details in self.card_types.items():
            if len(card_number) in details["lengths"]:
                for prefix in details["prefixes"]:
                    if card_number.startswith(prefix):
                        return card_type
        return "Unknown"

    def validate(self, card_number: str) -> dict:
        """Validate the card number and return info including card type and validity."""
        # Clean the card number (remove spaces, hyphens)
        cleaned_number = ''.join(filter(str.isdigit, card_number))
        
        if not cleaned_number:
            return {"card_number": card_number, "valid": False, "type": "Invalid"}
            
        is_valid = self.luhn_checksum_is_valid(cleaned_number)
        card_type = self.get_card_type(cleaned_number) if is_valid else "Invalid"
        
        return {
            "card_number": card_number,
            "valid": is_valid, 
            "type": card_type,
            "cleaned_number": cleaned_number
        }

# Convenience functions
def validate_card(card_number: str) -> dict:
    """Quick validation function."""
    validator = CardValidator()
    return validator.validate(card_number)

def is_valid_card(card_number: str) -> bool:
    """Returns True if card is valid."""
    return validate_card(card_number)["valid"]
