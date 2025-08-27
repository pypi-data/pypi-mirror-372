import unittest
from ai_safety_engine.policies.crypto_policies import CryptoRaiseExceptionPolicy
from ai_safety_engine.models import PolicyInput
from ai_safety_engine.exceptions import DisallowedOperation

class TestCryptoRaiseExceptionPolicy(unittest.TestCase):
    def test_crypto_content_raises_exception(self):
        """Test that crypto-related content raises the appropriate exception."""
        input_texts = [
            "Hello, I want to buy bitcoin",
            "How are the Ethereum prices?"
        ]
        policy_input = PolicyInput(input_texts=input_texts)

        # Execute the policy and expect a specific exception
        with self.assertRaises(DisallowedOperation) as context:
            CryptoRaiseExceptionPolicy.execute(policy_input)

        # Check that the exception message is correct
        self.assertIn("Cryptocurrency related content detected and operation stopped", str(context.exception))

    def test_clean_text_passes(self):
        """Test that non-crypto content is properly handled without raising exception."""
        input_texts = [
            "Hello, how are you?",
            "The weather is nice today"
        ]
        policy_input = PolicyInput(input_texts=input_texts)

        # Execute the policy - should not raise an exception
        try:
            rule_result, action_result, policy_output = CryptoRaiseExceptionPolicy.execute(policy_input)
        except DisallowedOperation as e:
            self.fail(f"Clean text should not raise DisallowedOperation, but got: {str(e)}")

        # Check that crypto content was not detected
        self.assertEqual(rule_result.confidence, 0.0)
        self.assertEqual(rule_result.content_type, "CRYPTO")
        self.assertFalse(rule_result.triggered_keywords)

        # Check that the action result indicates content is allowed
        self.assertIsNotNone(policy_output)
        self.assertTrue(hasattr(policy_output, 'action_output'))
        self.assertTrue('action_taken' in policy_output.action_output)
        self.assertEqual(policy_output.action_output['action_taken'], 'ALLOW')
