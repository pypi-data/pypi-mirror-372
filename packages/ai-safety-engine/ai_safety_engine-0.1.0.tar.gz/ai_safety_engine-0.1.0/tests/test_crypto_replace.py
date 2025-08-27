import unittest
from ai_safety_engine.policies.crypto_policies import CryptoReplace
from ai_safety_engine.models import PolicyInput

class TestCryptoReplace(unittest.TestCase):
    def test_crypto_content_replacement(self):
        """Test that crypto-related content is properly replaced."""
        input_texts = [
            "I want to buy Bitcoin",  # Starts with capital letter
            "Tell me about ETHEREUM and dogecoin",  # All caps and lowercase
            "btc and ETH trading"  # Abbreviations upper/lower case
        ]
        policy_input = PolicyInput(input_texts=input_texts)

        # Execute the policy
        rule_result, action_result, policy_output = CryptoReplace.execute(policy_input)

        # Rule should detect crypto content (5 keyword: bitcoin, ethereum, dogecoin, btc, eth)
        self.assertTrue(rule_result.confidence > 0.0)
        self.assertEqual(rule_result.content_type, "CRYPTO")
        detected_keywords = [k.lower() for k in rule_result.triggered_keywords]
        self.assertIn("bitcoin", detected_keywords)
        self.assertIn("ethereum", detected_keywords)
        self.assertIn("dogecoin", detected_keywords)
        self.assertIn("btc", detected_keywords)
        self.assertIn("eth", detected_keywords)

        # Action should replace and return modified texts
        self.assertEqual(policy_output.action_output.get('action_taken'), 'REPLACE')
        self.assertTrue(policy_output.action_output.get('success'))
        
        # Check that all crypto terms are replaced case-insensitively
        modified_texts = policy_output.output_texts
        self.assertEqual(modified_texts[0], "I want to buy NO_CRYPTO_CONTENT")
        self.assertEqual(modified_texts[1], "Tell me about NO_CRYPTO_CONTENT and NO_CRYPTO_CONTENT")
        self.assertEqual(modified_texts[2], "NO_CRYPTO_CONTENT and NO_CRYPTO_CONTENT NO_CRYPTO_CONTENT")

    def test_clean_text(self):
        """Ensure clean (non-crypto) texts are not modified."""
        input_texts = [
            "Hello, how are you?",
            "The weather is nice today"
        ]
        policy_input = PolicyInput(input_texts=input_texts)
        rule_result, action_result, policy_output = CryptoReplace.execute(policy_input)

        # Rule should not detect crypto content
        self.assertEqual(rule_result.confidence, 0.0)
        self.assertEqual(rule_result.content_type, "CRYPTO")
        self.assertFalse(rule_result.triggered_keywords)

        # Action should allow and return original texts without any changes
        self.assertEqual(policy_output.action_output.get('action_taken'), 'ALLOW')
        self.assertEqual(policy_output.output_texts, input_texts)
        self.assertTrue(policy_output.action_output.get('success'))

if __name__ == '__main__':
    unittest.main()
