"""
Policy class that combines rules and actions
"""

from typing import Optional, List
from .rule_base import RuleBase
from .action_base import ActionBase
from ..models import PolicyInput, RuleOutput, PolicyOutput, ActionOutput


class Policy:
    """Policy that combines a rule and an action"""
    
    def __init__(self, name: str, description: str, rule: RuleBase, action: ActionBase, 
                 language: str = "en",
                 language_identify_llm=None,
                 base_llm=None,
                 text_finder_llm=None,
                 language_identify_model: str = None,
                 base_model: str = None,
                 text_finder_model: str = None):
        self.name = name
        self.description = description
        self.rule = rule
        self.action = action
        self.language = language
        print("Now the langas is ", self.language)
        
        # Create LLM instances with models if specified
        from ..llm.upsonic_llm import UpsonicLLMProvider
        
        if language_identify_llm is None and language_identify_model:
            language_identify_llm = UpsonicLLMProvider(
                agent_name="Language Detection Agent", 
                model=language_identify_model
            )
        if base_llm is None and base_model:
            base_llm = UpsonicLLMProvider(
                agent_name="Base Operations Agent", 
                model=base_model
            )
        if text_finder_llm is None and text_finder_model:
            text_finder_llm = UpsonicLLMProvider(
                agent_name="Text Finder Agent", 
                model=text_finder_model
            )
        
        self.language_identify_llm = language_identify_llm
        self.base_llm = base_llm
        self.text_finder_llm = text_finder_llm
        
        # Update rule with text_finder_llm if provided
        if text_finder_llm and hasattr(self.rule, 'text_finder_llm'):
            self.rule.text_finder_llm = text_finder_llm
    
    def check(self, policy_input: PolicyInput) -> RuleOutput:
        """Check the input against the policy rule"""
        return self.rule.process(policy_input)
    

    
    def execute(self, policy_input: PolicyInput) -> tuple[RuleOutput, ActionOutput, PolicyOutput]:
        """Execute the full policy: check rule and take action"""
        rule_result = self.check(policy_input)

        print("I am the lang", self.language)
        action_result = self.action.execute_action(rule_result, policy_input.input_texts or [], self.language, 
                                        self.language_identify_llm, self.base_llm, self.text_finder_llm)
        return rule_result, action_result, action_result
    
    def __str__(self) -> str:
        return f"Policy(name='{self.name}', rule='{self.rule.name}', action='{self.action.name}')"
    
    def __repr__(self) -> str:
        return self.__str__()
