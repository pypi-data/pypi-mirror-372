import unittest
from ai_safety_engine.policies.crypto_policies import CryptoBlockPolicy
from ai_safety_engine.models import PolicyInput

class TestCryptoBlockPolicy(unittest.TestCase):
    def test_crypto_content_detection(self):
        """Test that crypto-related content is properly detected and handled."""
        input_texts = [
            "Hello, I want to buy bitcoin",
            "How are the Ethereum prices?"
        ]
        policy_input = PolicyInput(input_texts=input_texts)

        # Execute the policy
        rule_result, action_result, policy_output = CryptoBlockPolicy.execute(policy_input)

        # Check that crypto content was detected
        self.assertTrue(rule_result.confidence > 0.0)
        self.assertEqual(rule_result.content_type, "CRYPTO")
        self.assertTrue(len(rule_result.triggered_keywords) > 0)

        # Check that the action result contains appropriate flags and messages
        self.assertIsNotNone(policy_output)
        self.assertTrue(hasattr(policy_output, 'action_output'))
        self.assertTrue('action_taken' in policy_output.action_output)
        self.assertEqual(policy_output.action_output['action_taken'], 'BLOCK')

    def test_clean_text(self):
        """Test that non-crypto content is properly handled."""
        input_texts = [
            "Hello, how are you?",
            "The weather is nice today"
        ]
        policy_input = PolicyInput(input_texts=input_texts)

        # Execute the policy
        rule_result, action_result, policy_output = CryptoBlockPolicy.execute(policy_input)

        # Check that crypto content was not detected
        self.assertEqual(rule_result.confidence, 0.0)
        self.assertEqual(rule_result.content_type, "CRYPTO")
        self.assertFalse(rule_result.triggered_keywords)

        # Check that the action result indicates no crypto content
        self.assertIsNotNone(policy_output)
        self.assertTrue(hasattr(policy_output, 'action_output'))
        self.assertTrue('action_taken' in policy_output.action_output)
        self.assertEqual(policy_output.action_output['action_taken'], 'ALLOW')
