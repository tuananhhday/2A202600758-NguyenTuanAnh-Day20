"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from multi_agent_research_lab.core.config import Settings, get_settings
from multi_agent_research_lab.core.errors import StudentTodoError


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client skeleton."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion.

        Keep retry, timeout, and token logging here rather than inside agents.
        """

        if not self.settings.openai_api_key:
            raise StudentTodoError("Set OPENAI_API_KEY in .env before calling a real LLM")

        if self.settings.openai_api_key == "mock" or self.settings.app_env == "mock":
            # Return high-quality mock responses locally without API calls
            content = f"[Mock response for prompt: {user_prompt[:60]}...]"
            if "Researcher" in system_prompt:
                content = (
                    "[1] Anthropic: Building effective agents - https://www.anthropic.com/engineering/building-effective-agents\n"
                    "Snippet: Effective agentic systems should start simple, add orchestration only when it improves outcomes.\n"
                    "[2] OpenAI Agents SDK - https://developers.openai.com/api/docs/guides/agents/orchestration\n"
                    "Snippet: Agent handoffs work best when each role has structured input."
                )
            elif "Analyst" in system_prompt:
                content = (
                    "Key claims:\n"
                    "- Multi-agent systems improve clarity and citation coverage.\n"
                    "- Orchestration overhead increases latency.\n"
                    "Evidence risk: low; 2 sources available."
                )
            elif "Writer" in system_prompt:
                content = (
                    "# Research Report: Multi-Agent Systems\n\n"
                    "A multi-agent research system excels at structured reasoning and facts verification [1].\n"
                    "By separating concerns, agents reduce hallucinations compared to single-agent setups [2].\n\n"
                    "Sources:\n"
                    "[1] Anthropic: Building effective agents\n"
                    "[2] OpenAI Agents SDK orchestration"
                )
            elif "Critic" in system_prompt:
                content = "APPROVED"

            return LLMResponse(
                content=content,
                input_tokens=120,
                output_tokens=180,
            )


        payload = {
            "model": self.settings.openai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        }
        url = f"{self.settings.openai_base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "multi-agent-research-lab",
        }
        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.settings.timeout_seconds) as response:
                response_data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise StudentTodoError(
                f"LLM provider returned HTTP {exc.code}: {error_body}"
            ) from exc
        except URLError as exc:
            raise StudentTodoError(f"Could not reach LLM provider: {exc.reason}") from exc

        return _parse_chat_completion(response_data)


def _parse_chat_completion(response_data: dict[str, Any]) -> LLMResponse:
    choices = response_data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise StudentTodoError("LLM provider response did not contain choices")

    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise StudentTodoError("LLM provider response choice was not an object")

    message = first_choice.get("message")
    if not isinstance(message, dict):
        raise StudentTodoError("LLM provider response did not contain a message")

    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise StudentTodoError("LLM provider response did not contain text content")

    usage = response_data.get("usage")
    if not isinstance(usage, dict):
        usage = {}

    prompt_tokens = usage.get("prompt_tokens")
    completion_tokens = usage.get("completion_tokens")
    return LLMResponse(
        content=content,
        input_tokens=prompt_tokens if isinstance(prompt_tokens, int) else None,
        output_tokens=completion_tokens if isinstance(completion_tokens, int) else None,
    )
