import json
import requests
from typing import Optional, Union

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


def _normalize_proxy_url(u: str) -> str:
    """
    Возвращает корректный URL прокси.
    Если пользователь передал 'user:pass@host:port' без схемы,
    добавляем 'http://' по умолчанию.
    """
    if not u:
        return u
    u = u.strip()
    if u.startswith(("http://", "https://", "socks5://", "socks4://")):
        return u
    return "http://" + u


def _get_session(proxy: Union[bool, str]) -> requests.Session:
    """
    Настраиваем requests.Session с учётом прокси.

    Правила:
      - proxy=True  -> используем PROXY_HTTPS из _config.py (если задан)
      - proxy=False -> прокси отключён
      - proxy=str   -> используем переданный прокси (URL можно без схемы)
    """
    s = requests.Session()
    # Не брать прокси/сертификаты из переменных окружения:
    s.trust_env = False

    if proxy is True:
        if PROXY_HTTPS:
            p = _normalize_proxy_url(PROXY_HTTPS)
            s.proxies = {"http": p, "https": p}
        else:
            s.proxies = {}
    elif proxy is False:
        s.proxies = {}
    elif isinstance(proxy, str) and proxy.strip():
        p = _normalize_proxy_url(proxy)
        s.proxies = {"http": p, "https": p}
    else:
        s.proxies = {}

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
    proxy: Union[bool, str] = True,
) -> str:
    """
    Выполнить минимальный чат-запрос к OpenRouter.

    Аргумент proxy:
      - True  (по умолчанию): использовать PROXY_HTTPS из _config.py
      - False: выполнять запрос БЕЗ прокси
      - str  : использовать конкретный прокси; допустим как полный URL
               (http://..., https://..., socks5://...), так и 'user:pass@host:port'
               (в этом случае схема 'http://' будет добавлена автоматически)

    Примеры прокси (для удобства копипаста):
      - admin029iY:ZgXx5sCLUE@95.164.145.101:51523
      - admin029iY:ZgXx5sCLUE@95.164.145.243:51523
      - brunajacques:wC78ptKzqD@95.164.206.6:50100
      - joanasilvadeoliveira991:PrULmZwmnP@95.164.145.137:59100
    """
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

    s = _get_session(proxy)

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
