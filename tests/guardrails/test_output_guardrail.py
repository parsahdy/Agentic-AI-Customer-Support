import unittest

from agent.guardrails import (
    MaxOutputLengthRule,
    RequiredOutputRule,
    SensitiveDataRule,
)

from agent.config import MAX_OUTPUT_LENGTH


class TestOutputGuardrail(unittest.TestCase):

    def setUp(self):
        self.required_rule = RequiredOutputRule()
        self.max_length_rule = MaxOutputLengthRule()
        self.sensitive_rule = SensitiveDataRule()


    def codes(self, text: str) -> set[str]:
        return {v.code for v in self.SensitiveDataRule.find_violations(text)}


    def test_safe_output_has_no_violations(self):

        # Arrange
        text = (
            "Thank you! Your order has been confirmed "
            "and will be shipped within the next two days."
        )

        # Act
        required = self.required_rule.check(text)
        too_long = self.max_length_rule.check(text)
        sensitive = self.sensitive_rule.find_violations(text)

        # Assert
        self.assertIsNone(required)
        self.assertIsNone(too_long)
        self.assertEqual(sensitive, ())


    def test_empty_output(self):
        result = self.required_rule.check("")

        self.assertIsNotNone(result)
        self.assertEqual(result.code, "empty_output")


    def test_whitespace_only_output_is_empty(self):
        result = self.required_rule.check("   \n\t ")

        self.assertIsNotNone(result)
        self.assertEqual(result.code, "empty_output")


    def test_empty_output_has_no_sensitive_data(self):
        self.assertEqual(self.sensitive_rule.find_violations(""), ())


    def test_output_at_max_length_is_allowed(self):
        text = "a" * MAX_OUTPUT_LENGTH

        self.assertIsNone(self.max_length_rule.check(text))

    def test_output_over_max_length_is_blocked(self):
        text = "a" * (MAX_OUTPUT_LENGTH + 1)

        result = self.max_length_rule.check(text)

        self.assertIsNotNone(result)
        self.assertEqual(result.code, "output_too_long")

    def test_long_safe_text_has_no_false_positive(self):
        text = "Have a nice day. " * 5000

        self.assertEqual(self.sensitive_rule.find_violations(text), ())


    def test_valid_card_number_is_detected(self):
        text = "Your card number is 4111111111111111."

        self.assertIn("CARD_NUMBER", self.codes(text))

    def test_card_number_with_dashes_is_detected(self):
        text = "Your card number is 4111-1111-1111-1111."

        self.assertIn("CARD_NUMBER", self.codes(text))

    def test_card_number_failing_luhn_is_ignored(self):
        text = "Your tracking code is 1234567890123456."

        self.assertNotIn("CARD_NUMBER", self.codes(text))


    def test_card_number_failing_luhn_is_ignored(self):
        
        text = "Your tracking code is 1234567890123456."
        
        self.assertNotIn("CARD_NUMBER", self.codes(text))


    def test_iban_is_detected(self):
        text = "Your IBAN is IR062960000000100324200001."

        self.assertIn("IBAN", self.codes(text))

    def test_lowercase_iban_is_detected(self):
        text = "Your IBAN is ir062960000000100324200001."

        self.assertIn("IBAN", self.codes(text))


    def test_cvv2_is_detected(self):
        text = "The card CVV2: 457"

        self.assertIn("CARD_SECRET", self.codes(text))

    def test_expiry_date_is_detected(self):
        text = "Expiry date: 08/29"

        self.assertIn("CARD_SECRET", self.codes(text))

    def test_number_without_keyword_is_not_card_secret(self):
        text = "Your order total is 457 dollars."

        self.assertNotIn("CARD_SECRET", self.codes(text))


    def test_valid_national_id_is_detected(self):
        text = "Yes, the ID is 0499370899."

        self.assertIn("NATIONAL_ID", self.codes(text))

    def test_national_id_with_wrong_checksum_is_ignored(self):
        text = "Yes, the ID is 0499370890."

        self.assertNotIn("NATIONAL_ID", self.codes(text))


    def test_phone_number_is_detected(self):
        samples = [
            "Call me at 09123456789.",
            "Call me at +989123456789.",
            "Call me at ۰۹۱۲۳۴۵۶۷۸۹.",   
        ]
        for text in samples:
            with self.subTest(text=text):
                self.assertIn("PHONE_NUMBER", self.codes(text))


    def test_api_key_is_detected(self):
        fake_key = "sk-" + "a1B2c3D4e5F6g7H8i9J0k1L2"   
        text = f"Use this key: {fake_key}"

        self.assertIn("API_KEY", self.codes(text))


    def test_password_is_detected(self):
        text = "The admin password = abc123"

        self.assertIn("CREDENTIALS", self.codes(text))

    def test_database_connection_string_is_detected(self):
        text = "Connect with postgresql://user:pass@localhost/shop"

        self.assertIn("CREDENTIALS", self.codes(text))


if __name__ == "__main__":
    unittest.main()

