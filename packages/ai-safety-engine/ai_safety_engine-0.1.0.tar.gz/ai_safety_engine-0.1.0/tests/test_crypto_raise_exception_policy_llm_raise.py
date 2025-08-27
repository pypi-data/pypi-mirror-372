import unittest
from unittest.mock import patch, MagicMock
from ai_safety_engine.policies.crypto_policies import CryptoRaiseExceptionPolicy_LLM_Raise
from ai_safety_engine.models import PolicyInput
from ai_safety_engine.exceptions import DisallowedOperation

class TestCryptoRaiseExceptionPolicyLLMRaise(unittest.TestCase):
    
    @patch('ai_safety_engine.base.action_base.UpsonicLLMProvider')
    def test_exception_message_variability(self, mock_llm_class):
        """Run the policy twice on the same crypto-containing input and assert messages differ."""
        
        # Setup mock LLM
        mock_llm_instance = MagicMock()
        mock_llm_class.return_value = mock_llm_instance
        
        # Define expected mock responses
        expected_msg1 = "I apologize, but I cannot assist with cryptocurrency investment discussions as they may involve financial advice."
        expected_msg2 = "Sorry, cryptocurrency-related content is not permitted in this context due to regulatory considerations."
        
        # Mock generate_block_message to return different messages each time
        mock_llm_instance.generate_block_message.side_effect = [expected_msg1, expected_msg2]
        
        input_texts = [
            "I want to invest in Bitcoin and Ethereum for long term gains",
            "How can I buy BTC and ETH?"
        ]
        policy_input = PolicyInput(input_texts=input_texts)

        # First run
        with self.assertRaises(DisallowedOperation) as context1:
            CryptoRaiseExceptionPolicy_LLM_Raise.execute(policy_input)
        msg1 = str(context1.exception)

        # Second run
        with self.assertRaises(DisallowedOperation) as context2:
            CryptoRaiseExceptionPolicy_LLM_Raise.execute(policy_input)
        msg2 = str(context2.exception)

        # Messages should be non-empty strings
        self.assertIsInstance(msg1, str)
        self.assertIsInstance(msg2, str)
        self.assertTrue(len(msg1.strip()) > 0)
        self.assertTrue(len(msg2.strip()) > 0)
        
        # Test actual message content matches our mock responses
        self.assertEqual(msg1, expected_msg1, f"First exception message should match mock response. Got: '{msg1}', Expected: '{expected_msg1}'")
        self.assertEqual(msg2, expected_msg2, f"Second exception message should match mock response. Got: '{msg2}', Expected: '{expected_msg2}'")

        # The key variability check: messages should differ between runs
        self.assertNotEqual(msg1, msg2, "Expected the generated exception messages to differ between runs")
        
        # Verify LLM was called correctly (llm_raise_exception doesn't pass language parameter)
        self.assertEqual(mock_llm_instance.generate_block_message.call_count, 2)
        mock_llm_instance.generate_block_message.assert_called_with(
            "Providing investment advice is not a legally permitted operation."
        )

    @patch('ai_safety_engine.base.action_base.UpsonicLLMProvider')
    def test_clean_text(self, mock_llm_class):
        """Ensure clean (non-crypto) texts are allowed by the policy."""
        
        # Setup mock LLM (should not be called for clean text)
        mock_llm_instance = MagicMock()
        mock_llm_class.return_value = mock_llm_instance
        
        input_texts = [
            "Hello, how are you?",
            "The weather is nice today."
        ]
        policy_input = PolicyInput(input_texts=input_texts)
        
        # Execute the policy - should not raise an exception
        rule_result, action_result, policy_output = CryptoRaiseExceptionPolicy_LLM_Raise.execute(policy_input)

        # Rule should not detect crypto content
        self.assertEqual(rule_result.confidence, 0.0)
        self.assertEqual(rule_result.content_type, "CRYPTO")
        self.assertFalse(rule_result.triggered_keywords)

        # Action should allow and return original texts
        self.assertEqual(policy_output.action_output.get('action_taken'), 'ALLOW')
        self.assertEqual(policy_output.output_texts, input_texts)
        
        # Verify LLM was not called for clean text
        mock_llm_instance.generate_block_message.assert_not_called()

if __name__ == '__main__':
    unittest.main()
