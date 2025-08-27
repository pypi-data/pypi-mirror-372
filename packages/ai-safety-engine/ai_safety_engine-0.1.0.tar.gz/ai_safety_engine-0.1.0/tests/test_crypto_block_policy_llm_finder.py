import unittest
from unittest.mock import patch, MagicMock
from ai_safety_engine.policies.crypto_policies import CryptoBlockPolicy_LLM_Finder
from ai_safety_engine.models import PolicyInput

class TestCryptoBlockPolicyLLMFinder(unittest.TestCase):
    
    @patch('ai_safety_engine.base.rule_base.UpsonicLLMProvider')
    def test_crypto_content_detection(self, mock_llm_class):
        """Test that crypto-related content is properly detected and handled."""
        
        # Setup mock LLM
        mock_llm_instance = MagicMock()
        mock_llm_class.return_value = mock_llm_instance
        
        # Mock find_keywords to return crypto keywords
        mock_llm_instance.find_keywords.return_value = ["bitcoin", "ethereum"]
        
        # Mock detect_language to return English
        mock_llm_instance.detect_language.return_value = "en"
        
        input_texts = [
            "Hello, I want to buy bitcoin",
            "How are the Ethereum prices?"
        ]
        policy_input = PolicyInput(input_texts=input_texts)

        # Execute the policy
        rule_result, action_result, policy_output = CryptoBlockPolicy_LLM_Finder.execute(policy_input)

        # Check that crypto content was detected
        self.assertTrue(rule_result.confidence > 0.0)
        self.assertEqual(rule_result.content_type, "CRYPTO")
        self.assertTrue(len(rule_result.triggered_keywords) > 0)
        
        # Verify the detected keywords match our mock
        self.assertEqual(rule_result.triggered_keywords, ["bitcoin", "ethereum"])

        # Check that the action result contains appropriate flags and messages
        self.assertIsNotNone(policy_output)
        self.assertTrue(hasattr(policy_output, 'action_output'))
        self.assertTrue('action_taken' in policy_output.action_output)
        self.assertEqual(policy_output.action_output['action_taken'], 'BLOCK')
        
        # Verify LLM was called correctly
        mock_llm_instance.find_keywords.assert_called_once_with("Crypto", "Hello, I want to buy bitcoin How are the Ethereum prices?", language="en")
        mock_llm_instance.detect_language.assert_called_once_with("Hello, I want to buy bitcoin How are the Ethereum prices?")

    @patch('ai_safety_engine.base.rule_base.UpsonicLLMProvider')
    def test_clean_text(self, mock_llm_class):
        """Test that non-crypto content is properly handled."""
        
        # Setup mock LLM
        mock_llm_instance = MagicMock()
        mock_llm_class.return_value = mock_llm_instance
        
        # Mock find_keywords to return empty list (no crypto content)
        mock_llm_instance.find_keywords.return_value = []
        
        # Mock detect_language to return English
        mock_llm_instance.detect_language.return_value = "en"
        
        input_texts = [
            "Hello, how are you?",
            "The weather is nice today"
        ]
        policy_input = PolicyInput(input_texts=input_texts)

        # Execute the policy
        rule_result, action_result, policy_output = CryptoBlockPolicy_LLM_Finder.execute(policy_input)

        # Check that crypto content was not detected
        self.assertEqual(rule_result.confidence, 0.0)
        self.assertEqual(rule_result.content_type, "CRYPTO")
        self.assertFalse(rule_result.triggered_keywords)

        # Check that the action result indicates no crypto content
        self.assertIsNotNone(policy_output)
        self.assertTrue(hasattr(policy_output, 'action_output'))
        self.assertTrue('action_taken' in policy_output.action_output)
        self.assertEqual(policy_output.action_output['action_taken'], 'ALLOW')
        
        # Verify LLM was called correctly
        mock_llm_instance.find_keywords.assert_called_once_with("Crypto", "Hello, how are you? The weather is nice today", language="en")
        mock_llm_instance.detect_language.assert_called_once_with("Hello, how are you? The weather is nice today")

if __name__ == '__main__':
    unittest.main()
