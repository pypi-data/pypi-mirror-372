"""
Generic OpenAI API client abstraction.
"""

import json
import os
from typing import Any

from openai import OpenAI


class OpenAIClient:
    """Generic abstraction layer for OpenAI API interactions."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-5-mini"):
        """
        Initialize the OpenAI client.

        Args:
            api_key: OpenAI API key (if None, will try to get from environment)
            model: OpenAI model to use for generation

        Raises:
            ValueError: If no API key is provided or found in environment
        """
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_response(
        self, user_prompt: str, system_prompt: str = "You are a helpful assistant.", max_retries: int = 3, **kwargs
    ) -> str:
        """
        Generate a response using OpenAI's API.

        Args:
            user_prompt: The user prompt to send to the model
            system_prompt: The system prompt to use (configurable)
            max_retries: Maximum number of retry attempts
            **kwargs: Additional parameters to pass to the OpenAI API

        Returns:
            Response content from OpenAI

        Raises:
            Exception: If API call fails after max retries
        """
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    **kwargs,
                )
                return response.choices[0].message.content.strip()

            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to generate response after {max_retries} attempts: {e!s}") from e
                continue

        raise Exception(f"Failed to generate response after {max_retries} attempts")

    def generate_json_response(
        self,
        user_prompt: str,
        system_prompt: str = "You are a helpful assistant that provides structured responses in valid JSON format.",
        max_retries: int = 3,
        **kwargs,
    ) -> Any:
        """
        Generate a JSON response using OpenAI's API.

        Args:
            user_prompt: The user prompt to send to the model
            system_prompt: The system prompt to use (configurable)
            max_retries: Maximum number of retry attempts
            **kwargs: Additional parameters to pass to the OpenAI API

        Returns:
            Parsed JSON response from OpenAI

        Raises:
            Exception: If API call fails after max retries or JSON parsing fails
        """
        response_text = self.generate_response(
            user_prompt=user_prompt, system_prompt=system_prompt, max_retries=max_retries, **kwargs
        )

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {response_text}") from e

    def generate_questions(
        self,
        chunk_text: str,
        prompt_template: str,
        system_prompt: str = "You are a helpful assistant that generates high-quality questions based on provided context. Always respond with valid JSON.",
        max_retries: int = 3,
    ) -> list[dict[str, str]]:
        """
        Generate questions that can be answered by the given chunk using OpenAI's API.

        This is a convenience method that maintains compatibility with existing code.

        Args:
            chunk_text: The text chunk to generate questions for (includes metadata)
            prompt_template: Template string with {chunk_text} placeholder
            system_prompt: The system prompt to use (configurable)
            max_retries: Maximum number of retry attempts

        Returns:
            List of dictionaries with 'question' and 'answer' keys

        Raises:
            Exception: If API call fails after max retries
        """
        user_prompt = prompt_template.format(chunk_text=chunk_text)

        questions = self.generate_json_response(
            user_prompt=user_prompt, system_prompt=system_prompt, max_retries=max_retries
        )

        # Validate and format the response
        if isinstance(questions, list):
            # Empty list is a valid response when chunk is not suitable for questions
            if len(questions) == 0:
                return []

            valid_questions = []
            for q in questions:
                if isinstance(q, dict) and "question" in q:
                    valid_questions.append(
                        {
                            "question": q["question"],
                        }
                    )

            return valid_questions

        raise Exception("Failed to generate valid questions from response")
