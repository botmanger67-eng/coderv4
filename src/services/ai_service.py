from typing import Optional
import openai
from src.core.config import settings
from src.core.logger import logger


class AIService:
    """Service for interacting with DeepSeek API."""

    def __init__(self) -> None:
        """Initialize AI service with DeepSeek configuration."""
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.model = settings.DEEPSEEK_MODEL
        self.max_tokens = settings.DEEPSEEK_MAX_TOKENS
        self.temperature = settings.DEEPSEEK_TEMPERATURE

        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY is not configured")

        openai.api_key = self.api_key
        openai.base_url = self.base_url

    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Generate a response from DeepSeek API.

        Args:
            prompt: User prompt to send to the model.
            system_prompt: Optional system prompt for context.
            max_tokens: Maximum tokens in response. Defaults to config value.
            temperature: Response temperature. Defaults to config value.

        Returns:
            Generated text response.

        Raises:
            openai.APIError: If API call fails.
            ValueError: If prompt is empty.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            logger.debug(f"Sending request to DeepSeek API with model: {self.model}")
            response = await openai.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from DeepSeek API")

            logger.debug("Successfully received response from DeepSeek API")
            return content

        except openai.APIError as e:
            logger.error(f"DeepSeek API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in AI service: {e}")
            raise

    async def generate_code_review(
        self,
        code: str,
        language: str = "python",
    ) -> str:
        """Generate a code review using DeepSeek API.

        Args:
            code: Source code to review.
            language: Programming language of the code.

        Returns:
            Code review text with suggestions and improvements.
        """
        system_prompt = (
            f"You are an expert {language} code reviewer. "
            "Provide constructive feedback on code quality, "
            "potential bugs, performance issues, and best practices."
        )
        prompt = f"Please review the following {language} code:\n\n```{language}\n{code}\n```"

        return await self.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
        )

    async def generate_summary(
        self,
        text: str,
        max_length: int = 150,
    ) -> str:
        """Generate a summary of the given text.

        Args:
            text: Text to summarize.
            max_length: Maximum length of summary in words.

        Returns:
            Generated summary text.
        """
        system_prompt = (
            "You are a text summarization assistant. "
            f"Provide a concise summary in {max_length} words or less."
        )
        prompt = f"Please summarize the following text:\n\n{text}"

        return await self.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_length * 2,
        )

    async def generate_commit_message(
        self,
        diff: str,
    ) -> str:
        """Generate a commit message from a git diff.

        Args:
            diff: Git diff text.

        Returns:
            Generated commit message.
        """
        system_prompt = (
            "You are an expert at writing git commit messages. "
            "Generate a concise, descriptive commit message following "
            "conventional commits format."
        )
        prompt = f"Generate a commit message for the following diff:\n\n{diff}"

        return await self.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=100,
        )