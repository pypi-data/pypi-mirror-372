import unittest
from unittest.mock import patch, MagicMock
from ai_safety_engine.policies.phone_policies import AnonymizePhoneNumbersPolicy_LLM_Finder
from ai_safety_engine.models import PolicyInput

class TestAnonymizePhoneNumbersPolicyLLMFinder(unittest.TestCase):
    
    @patch('ai_safety_engine.base.rule_base.UpsonicLLMProvider')
    def test_phone_number_detection_and_anonymization(self, mock_llm_class):
        """Test that phone numbers are properly detected and anonymized."""
        
        # Setup mock LLM
        mock_llm_instance = MagicMock()
        mock_llm_class.return_value = mock_llm_instance
        
        # Mock find_keywords to return phone numbers
        mock_llm_instance.find_keywords.return_value = ["5551234567", "0555-123-4567", "+90 555 123 4567"]
        
        # Mock detect_language to return English
        mock_llm_instance.detect_language.return_value = "en"
        
        input_texts = [
            "My number is 5551234567",
            "Call me at 0555-123-4567 or +90 555 123 4567"
        ]
        policy_input = PolicyInput(input_texts=input_texts)
        
        rule_result, action_result, policy_output = AnonymizePhoneNumbersPolicy_LLM_Finder.execute(policy_input)
        
        # Verify the rule detected phone numbers
        self.assertTrue(rule_result.confidence > 0.0)
        self.assertEqual(rule_result.content_type, "PHONE_NUMBER")
        self.assertEqual(rule_result.triggered_keywords, ["5551234567", "0555-123-4567", "+90 555 123 4567"])
        
        # Verify action was taken
        self.assertEqual(policy_output.action_output['action_taken'], 'ANONYMIZE')
        
        # Verify phone numbers are anonymized (not present in output)
        for phone in ["5551234567", "0555-123-4567", "+90 555 123 4567"]:
            self.assertFalse(any(phone in out for out in policy_output.output_texts))
        
        # Verify output is different from input (anonymization occurred)
        self.assertTrue(any(out != inp for out, inp in zip(policy_output.output_texts, input_texts)))
        
        # Verify LLM was called correctly
        mock_llm_instance.find_keywords.assert_called_once_with("Phone Number", "My number is 5551234567 Call me at 0555-123-4567 or +90 555 123 4567", language="en")
        mock_llm_instance.detect_language.assert_called_once_with("My number is 5551234567 Call me at 0555-123-4567 or +90 555 123 4567")

    @patch('ai_safety_engine.base.rule_base.UpsonicLLMProvider')
    def test_clean_text_allowed(self, mock_llm_class):
        """Test that non-phone content is properly allowed."""
        
        # Setup mock LLM
        mock_llm_instance = MagicMock()
        mock_llm_class.return_value = mock_llm_instance
        
        # Mock find_keywords to return empty list (no phone numbers)
        mock_llm_instance.find_keywords.return_value = []
        
        # Mock detect_language to return English
        mock_llm_instance.detect_language.return_value = "en"
        
        input_texts = ["Hello, how are you?", "The weather is nice today"]
        policy_input = PolicyInput(input_texts=input_texts)
        
        rule_result, action_result, policy_output = AnonymizePhoneNumbersPolicy_LLM_Finder.execute(policy_input)
        
        # Verify the rule detected no phone numbers
        self.assertEqual(rule_result.confidence, 0.0)
        self.assertEqual(rule_result.content_type, "PHONE_NUMBER")
        self.assertFalse(rule_result.triggered_keywords)
        
        # Verify action allows content
        self.assertEqual(policy_output.action_output['action_taken'], 'ALLOW')
        self.assertEqual(policy_output.output_texts, input_texts)
        
        # Verify LLM was called correctly
        mock_llm_instance.find_keywords.assert_called_once_with("Phone Number", "Hello, how are you? The weather is nice today", language="en")
        mock_llm_instance.detect_language.assert_called_once_with("Hello, how are you? The weather is nice today")

if __name__ == "__main__":
    unittest.main()