import os
from typing import Literal, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from questions_cli_app import config


class LLMClient:
    def __init__(self, provider: Literal["openai", "any"] = "openai", model: Optional[str] = None):
        self.provider = provider
        self.model = model or os.getenv("LLM_MODEL") or config.MODEL_NAME
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        self.timeout = float(os.getenv("LLM_TIMEOUT_SECONDS", "60"))
        self.http2_env = os.getenv("LLM_HTTP2", "0") == "1"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8), reraise=True)
    def classify_text(self, text: str) -> Literal["question", "keyword"]:
        prompt = config.CLASSIFICATION_PROMPT_TEMPLATE.replace("{input_text}", text)
        result = self._complete(prompt)
        out = result.strip().lower()
        if "question" in out and "keyword" not in out:
            return "question"
        if "keyword" in out and "question" not in out:
            return "keyword"
        return "keyword"

    def _complete(self, prompt: str) -> str:
        if self.provider == "openai":
            return self._openai_complete(prompt)
        return self._openai_complete(prompt)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10), retry=retry_if_exception_type(httpx.HTTPError), reraise=True)
    def _openai_complete(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("LLM_API_KEY is not set. Export LLM_API_KEY to enable generation.")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "questions-cli/0.1",
        }
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You answer with minimal content only."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.0,
            "max_tokens": 512,
        }
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
        # Only enable HTTP/2 if explicitly requested and 'h2' is installed
        http2_flag = False
        if self.http2_env:
            try:
                import h2  # type: ignore  # noqa: F401
                http2_flag = True
            except Exception:
                http2_flag = False
        with httpx.Client(timeout=self.timeout, limits=limits, http2=http2_flag) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"] 