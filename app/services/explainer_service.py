"""
ExplainerService: Core service for code explanation using AutoGen agents.
Optimized for CodeLlama 7B-instruct model.
"""

import autogen
from typing import Dict, List
import json
import logging

from app.agents.prompts import EXPLAINER_SYSTEM_PROMPT, CLARIFIER_SYSTEM_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExplainerService:
    """
    Service for explaining Python code using AutoGen agents.
    Optimized for CodeLlama 7B-instruct model.
    """

    def __init__(self, ollama_base_url: str, model_name: str):
        """
        Initialize the service with LLM configuration.
        Optimized settings for 7B-instruct model.
        """
        self.config_list = [
            {
                "model": model_name,
                "base_url": f"{ollama_base_url}/v1",
                "api_type": "open_ai",
                "api_key": "sk-xxx",  # Dummy key for OpenAI compatibility
                "temperature": 0.3,  # Lower temperature for more focused responses
                "max_tokens": 2048,  # Increased for more detailed explanations
            }
        ]
        self._setup_agents()

    def _setup_agents(self) -> None:
        """
        Set up AutoGen agents with optimized configurations for 7B-instruct model.
        """
        llm_config = {
            "config_list": self.config_list,
            "cache_seed": 42,
            "temperature": 0.3,
        }

        self.clarifier_agent = autogen.AssistantAgent(
            name="ClarifierAgent",
            system_message=CLARIFIER_SYSTEM_PROMPT,
            llm_config=llm_config,
        )

        self.explainer_agent = autogen.AssistantAgent(
            name="ExplainerAgent",
            system_message=EXPLAINER_SYSTEM_PROMPT,
            llm_config=llm_config,
        )

        self.user_proxy_agent = autogen.UserProxyAgent(
            name="UserProxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2,
            code_execution_config=False,
            default_auto_reply="Thank you for the explanation.",
            is_termination_msg=lambda x: "thank you" in x.get("content", "").lower()
        )

    async def explain_code(self, code_snippet: str) -> str:
        """
        Generate explanation for the given code snippet.
        Optimized prompting for 7B-instruct model.
        """
        try:
            logger.info("Starting code explanation process")
            
            # Format the code snippet
            formatted_code = code_snippet.strip()
            logger.info(f"Code snippet length: {len(formatted_code)} characters")

            # Step 1: Get clarification points with instruct format
            clarification_task = f"""[INST] You are a Python code reviewer. Review this code and list any parts that need clarification:

```python
{formatted_code}
```

Focus on:
1. Algorithm logic
2. Variable usage
3. Edge cases
4. Performance considerations

List your findings as bullet points. If the code is clear, state that it's straightforward. [/INST]"""
            
            logger.info("Requesting clarification points")
            await self.user_proxy_agent.a_initiate_chat(
                self.clarifier_agent,
                message=clarification_task,
                max_turns=1
            )
            
            clarification_points = self.user_proxy_agent.last_message(self.clarifier_agent)
            if not clarification_points:
                logger.warning("No response received from clarifier agent")
                clarification_content = "Code appears straightforward."
            else:
                clarification_content = clarification_points.get("content", "Code appears straightforward.")
            
            logger.info("Received clarification points")

            # Step 2: Prepare explanation task
            explanation_task = f"""[INST] You are a Python code explainer. Explain this code clearly and comprehensively:

```python
{formatted_code}
```

Consider these points from the code review:
{clarification_content}

Provide your explanation in this structure:
1. Purpose and Overview
2. Algorithm Explanation
3. Key Components
4. Time and Space Complexity
5. Example Execution Flow

Make it clear and detailed. [/INST]"""

            logger.info("Requesting explanation")
            await self.user_proxy_agent.a_initiate_chat(
                self.explainer_agent,
                message=explanation_task,
                max_turns=1
            )

            explanation = self.user_proxy_agent.last_message(self.explainer_agent)
            if not explanation:
                logger.warning("No response received from explainer agent")
                return "I apologize, but I couldn't generate an explanation. Please try again."
            
            explanation_content = explanation.get("content", "").strip()
            if not explanation_content:
                logger.warning("Empty explanation received")
                return "I apologize, but I couldn't generate a meaningful explanation. Please try again."
            
            logger.info("Successfully generated explanation")
            return explanation_content

        except Exception as e:
            logger.error(f"Error during code explanation: {str(e)}", exc_info=True)
            return f"An error occurred while analyzing the code: {str(e)}. Please try again or check if the code is properly formatted." 