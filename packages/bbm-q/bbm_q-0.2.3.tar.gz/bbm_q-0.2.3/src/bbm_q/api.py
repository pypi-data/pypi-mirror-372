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

    Руководство:
    1. !pip install bbm-q или в случае проблем с прокси: !pip install --proxy <прокси> bbm-q
    2. from bbm_q import q, show, find
        q - выполняет запрос к openrouter API и возвращает результат (аргументы prompt (str), model (str), proxy (bool/str)) - q("реши то-то-то") или q("реши то-то-то", model="model2", proxy=False)
        show - показать/скрыть выделенную ячейку - show(True/False), True - если скрыть, False - показать. СКРЫВАЕТ ТЕКСТ ИМЕННО В ВЫДЕЛЕННОЙ ЯЧЕЙКЕ, ТО ЕСТЬ ЕСЛИ СМЕЩАТЬ ФОКУС, ТО НОВАЯ ЯЧЕЙКА БУДЕТ СКРЫТА А СТАРАЯ ВИДНА.
        find - оффлайн поиск - find("что искать", top_k=3) - ищет по локальной базе соответствующий текст и возвращает top_k наиболее подходящих. top_k - сколько результатов вернуть, по умолчанию 1.

        q - может принимать разные модели в model, по умолчанию model1.
          - model1 -> GPT-5
          - model2 -> gemini 2.5 pro
          - model3 -> claude sonnet
          - model4 -> deepseek 3.1
          - model5 -> deepseek 3

        Использование: q("реши то-то-то", model="model3")

        Важно:
        Иногда дипсик модели могут не работать на пендосских проксях, если не работает - отключайте прокси (proxy=False).
        
    Список прокси (НОВЫЕ):
      -  C1E6n4:xjtycY@45.143.245.193:8000 Россия
      -  Kd98tg:XWFbGM@185.71.215.82:8000 Австрия
      -  GpXB0M:z2L40A@89.191.232.111:8000 Польша
      -  r0hoHu:5DM8re@200.10.39.70:8000 Америка
      -  jZAV8A:HZ2T6v@193.58.110.45:8000 Франция

    Список прокси (СТАРЫЕ):
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
