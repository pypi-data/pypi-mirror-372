import unittest
from ai_safety_engine.policies.phone_policies import AnonymizePhoneNumbersPolicy
from ai_safety_engine.models import PolicyInput

class TestAnonymizePhoneNumbersPolicy(unittest.TestCase):
    def test_phone_number_detection_and_anonymization(self):
        input_texts = [
            "My number is 5551234567",
            "Call me at 0555-123-4567"
        ]
        policy_input = PolicyInput(input_texts=input_texts)
        # Use full policy execution (rule + action) instead of testing internals separately
        rule_result, action_result, policy_output = AnonymizePhoneNumbersPolicy.execute(policy_input)
        self.assertEqual(rule_result.confidence, 1.0)
        self.assertEqual(rule_result.content_type, "PHONE_NUMBER")
        self.assertGreaterEqual(len(rule_result.triggered_keywords), 1)
        self.assertIn("5551234567", " ".join(rule_result.triggered_keywords))
        self.assertTrue(any("0555-123-4567".replace("-", "") in kw.replace("-", "") for kw in rule_result.triggered_keywords))
        # PolicyOutput checks from execute()
        self.assertNotIn("5551234567", " ".join(policy_output.output_texts))
        self.assertNotIn("0555-123-4567", " ".join(policy_output.output_texts))
        self.assertEqual(policy_output.action_output["action_taken"], "ANONYMIZE")
        self.assertTrue(policy_output.action_output["success"])

    def test_clean_text(self):
        input_texts = [
            "Hello, how are you?",
            "The weather is nice today"
        ]
        policy_input = PolicyInput(input_texts=input_texts)
        # Use full policy execution
        rule_result, action_result, policy_output = AnonymizePhoneNumbersPolicy.execute(policy_input)
        self.assertEqual(rule_result.confidence, 0.0)
        self.assertEqual(rule_result.content_type, "PHONE_NUMBER")
        self.assertFalse(rule_result.triggered_keywords)
        # PolicyOutput checks from execute()
        self.assertEqual(policy_output.output_texts, input_texts)
        self.assertEqual(policy_output.action_output["action_taken"], "ALLOW")
        self.assertTrue(policy_output.action_output["success"])

if __name__ == "__main__":
    unittest.main()
