import unittest
from unittest.mock import patch, MagicMock
from ai_safety_engine.policies.crypto_policies import CryptoRule, Policy, CryptoBlockAction, CryptoBlockPolicy
from ai_safety_engine.models import PolicyInput

# Bu policy static şekilde tarama yapar ve eğer kripto keywordleri bulursa direk block aksiyonu dönderir. 
CryptoBlockPolicy_2 = Policy(
    name="Crypto Block Policy",
    description="Designed for financial institutions to block cryptocurrency discussions",
    rule=CryptoRule(),
    action=CryptoBlockAction(),
    language = "tr"  # Default language for this rule
)

CryptoBlockPolicy_3 = Policy(
    name="Crypto Block Policy",
    description="Designed for financial institutions to block cryptocurrency discussions",
    rule=CryptoRule(),
    action=CryptoBlockAction(),
    language = "auto"  # Default language for this rule
)

class TestCryptoBlockPolicyLanguage(unittest.TestCase):
    
    @patch('ai_safety_engine.base.action_base.UpsonicLLMProvider')
    def test_crypto_content_detection_language_default(self, mock_llm_class):
        """Test that crypto-related content is properly detected and handled with default language."""
        
        # Setup mock LLM (should not be called for default language since no translation needed)
        mock_llm_instance = MagicMock()
        mock_llm_class.return_value = mock_llm_instance
        
        input_texts = [
            "Selam bitcoin almak istiyorum"
        ]
        policy_input = PolicyInput(input_texts=input_texts)

        print("LANGG is", CryptoBlockPolicy.language)

        rule_result_1, action_result_1, policy_output_1 = CryptoBlockPolicy.execute(policy_input)

        self.assertEqual(policy_output_1.action_output["message"], "Cryptocurrency related content detected and blocked.")
        
        # Verify LLM was not called for default language (no translation needed)
        mock_llm_instance.translate_text.assert_not_called()

    @patch('ai_safety_engine.base.action_base.UpsonicLLMProvider')
    def test_crypto_content_detection_language_turkish(self, mock_llm_class):
        """Test that crypto-related content is properly detected and handled with Turkish language."""
        
        # Setup mock LLM
        mock_llm_instance = MagicMock()
        mock_llm_class.return_value = mock_llm_instance
        
        # Mock translate_text to return Turkish translation
        mock_llm_instance.translate_text.return_value = "Kripto para ile ilgili içerik tespit edildi ve engellendi."
        
        input_texts = [
            "Selam bitcoin almak istiyorum"
        ]

        policy_input_2 = PolicyInput(input_texts=input_texts)

        rule_result_2, action_result_2, policy_output_2 = CryptoBlockPolicy_2.execute(policy_input_2)

        # Verify the message is translated (not the default English message)
        self.assertNotEqual(policy_output_2.action_output["message"], "Cryptocurrency related content detected and blocked.")
        self.assertEqual(policy_output_2.action_output["message"], "Kripto para ile ilgili içerik tespit edildi ve engellendi.")
        
        # Verify LLM was called for translation
        mock_llm_instance.translate_text.assert_called_once_with(
            "Cryptocurrency related content detected and blocked.", 
            "tr"
        )

    @patch('ai_safety_engine.base.action_base.UpsonicLLMProvider')
    def test_crypto_content_detection_language_auto(self, mock_llm_class):
        """Test that crypto-related content is properly detected and handled with auto language detection."""
        
        # Setup mock LLM
        mock_llm_instance = MagicMock()
        mock_llm_class.return_value = mock_llm_instance
        
        # Mock detect_language to return Turkish
        mock_llm_instance.detect_language.return_value = "tr"
        
        # Mock translate_text to return Turkish translation
        mock_llm_instance.translate_text.return_value = "Kripto para ile ilgili içerik tespit edildi ve engellendi."
        
        input_texts = [
            "Selam bitcoin almak istiyorum"
        ]

        policy_input = PolicyInput(input_texts=input_texts)

        rule_result, action_result, policy_output = CryptoBlockPolicy_3.execute(policy_input)

        # Verify the message is translated (not the default English message)
        self.assertNotEqual(policy_output.action_output["message"], "Cryptocurrency related content detected and blocked.")
        self.assertEqual(policy_output.action_output["message"], "Kripto para ile ilgili içerik tespit edildi ve engellendi.")
        
        # Verify LLM was called for language detection and translation
        mock_llm_instance.detect_language.assert_called_once_with("Selam bitcoin almak istiyorum")
        mock_llm_instance.translate_text.assert_called_once_with(
            "Cryptocurrency related content detected and blocked.", 
            "tr"
        )

if __name__ == '__main__':
    unittest.main()
