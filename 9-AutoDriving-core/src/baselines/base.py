"""
Base class for all baseline methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json
import time


class BaselineMethod(ABC):
    """Abstract base class for travel planning baseline methods."""

    def __init__(self, llm_client, method_name: str):
        """
        Initialize baseline method.

        Args:
            llm_client: LLM client instance (from llm_client.py)
            method_name: Name of this baseline method (e.g., "b0_direct")
        """
        self.llm_client = llm_client
        self.method_name = method_name
        self.call_history = []

    @abstractmethod
    def build_prompt(self, query: Dict[str, Any]) -> str:
        """
        Build the prompt for this baseline method.

        Args:
            query: Dict with keys like org, dest, days, people_number

        Returns:
            Prompt string to send to LLM
        """
        pass

    def generate_plan(self, query: Dict[str, Any], temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate a travel plan for the given query.

        Args:
            query: Travel query dict
            temperature: Sampling temperature

        Returns:
            Dict with keys:
                - plan: List of day plans (or None if generation failed)
                - raw_response: Raw LLM response text
                - success: Whether generation succeeded
                - error: Error message if failed
                - metadata: Additional info (tokens, time, etc.)
        """
        start_time = time.time()

        try:
            # Build prompt
            prompt = self.build_prompt(query)

            # Call LLM
            response = self.llm_client.call(
                prompt=prompt,
                temperature=temperature,
                max_tokens=4096
            )

            # Parse response
            plan = self.parse_response(response['content'])

            # Record call
            call_record = {
                'query': query,
                'prompt': prompt,
                'response': response,
                'plan': plan,
                'time': time.time() - start_time
            }
            self.call_history.append(call_record)

            return {
                'plan': plan,
                'raw_response': response['content'],
                'success': plan is not None,
                'error': None if plan is not None else "Failed to parse valid plan",
                'metadata': {
                    'method': self.method_name,
                    'tokens': response.get('usage', {}),
                    'time_seconds': time.time() - start_time,
                    'temperature': temperature
                }
            }

        except Exception as e:
            return {
                'plan': None,
                'raw_response': None,
                'success': False,
                'error': str(e),
                'metadata': {
                    'method': self.method_name,
                    'time_seconds': time.time() - start_time
                }
            }

    def parse_response(self, response_text: str) -> List[List[Dict[str, Any]]]:
        """
        Parse LLM response into plan format.

        Expected format: List of days, each day is a list of dicts with keys:
            days, current_city, transportation, breakfast, attraction,
            lunch, dinner, accommodation

        Args:
            response_text: Raw LLM response

        Returns:
            Parsed plan or None if parsing failed
        """
        try:
            # Try to find JSON in response
            # Look for patterns like ```json ... ``` or direct JSON
            text = response_text.strip()

            # Remove markdown code blocks if present
            if '```json' in text:
                start = text.find('```json') + 7
                end = text.find('```', start)
                text = text[start:end].strip()
            elif '```' in text:
                start = text.find('```') + 3
                end = text.find('```', start)
                text = text[start:end].strip()

            # Try to parse as JSON
            plan = json.loads(text)

            # Validate basic structure
            if isinstance(plan, list):
                # Check if it's already in correct format
                if all(isinstance(day, list) for day in plan):
                    return plan
                # Maybe it's just a flat list of day dicts
                elif all(isinstance(day, dict) for day in plan):
                    return [plan]  # Wrap in outer list

            return None

        except (json.JSONDecodeError, ValueError, TypeError):
            return None

    def save_cache(self, filepath: str):
        """Save call history to file for replay."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.call_history, f, ensure_ascii=False, indent=2)

    def load_cache(self, filepath: str):
        """Load call history from file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.call_history = json.load(f)
