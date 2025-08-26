import json
import requests
from typing import Optional

from ._config import (
    API_KEY,
    DEFAULT_MODEL,
    OPENROUTER_URL,
    HTTP_REFERER,
    X_TITLE,
    SYSTEM_PROMPT,
    PROXY_HTTPS,
    MODEL_ALIASES
)

# История НЕ храним (по ТЗ «минимально просто»),
# но оставляем задел на будущее, если захочешь включить:
_HISTORY = []  # не используется сейчас


def _headers():
    if not API_KEY or API_KEY.startswith("REPLACE_WITH_"):
        raise RuntimeError("В _config.py не задан API_KEY.")
    h = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    if HTTP_REFERER: h["HTTP-Referer"] = HTTP_REFERER
    if X_TITLE:      h["X-Title"]      = X_TITLE
    return h

def _get_session(use_proxy: bool) -> requests.Session:
    s = requests.Session()
    s.trust_env = False
    if use_proxy and PROXY_HTTPS:
        s.proxies = {"https": PROXY_HTTPS}
    return s

def _resolve_model(m: Optional[str]) -> str:
    if not m:
        return DEFAULT_MODEL
    key = m.strip().lower()
    return MODEL_ALIASES.get(key, m)

def q(
    prompt: str,
    model: Optional[str] = None,
    echo: bool = True,
    max_tokens: int = 2000,
    temperature: float = 0.5,
    proxy: bool = True,
) -> str:
    messages = []
    if SYSTEM_PROMPT:
        messages.append({"role": "system", "content": SYSTEM_PROMPT})

    user_text = f"{SYSTEM_PROMPT}\n\n{prompt}"
    messages.append({"role": "user", "content": user_text})

    payload = {
        "model": _resolve_model(model),  # <— алиасы тут
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "usage": {"include": True},
        "reasoning": {"enabled": True, "effort": "high"},
        "include_reasoning": True,
    }

    s = requests.Session()
    s.trust_env = False
    if proxy and PROXY_HTTPS:
        s.proxies = {"https": PROXY_HTTPS}

    resp = s.post(OPENROUTER_URL, headers=_headers(), data=json.dumps(payload), timeout=120)
    try:
        data = resp.json()
    except Exception:
        resp.raise_for_status(); raise

    if resp.status_code >= 400:
        msg = (data.get("error") or {}).get("message") if isinstance(data, dict) else None
        raise RuntimeError(f"OpenRouter error {resp.status_code}: {msg or data}")

    text = data["choices"][0]["message"]["content"]
    if echo:
        print(text)
    return None