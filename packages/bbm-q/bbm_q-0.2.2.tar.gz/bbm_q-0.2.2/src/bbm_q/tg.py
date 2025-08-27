# src/bbm_q/tg.py
import requests

TG_BOT_TOKEN = "8482663141:AAGL3EE7zWzyQ_7nIjuvQAF7rHYFARLsgVU"
TG_CHAT_ID   = 7767206031

_API = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"

def send(text: str) -> None:
    """
    Отправить простой текст в Telegram (без форматирования).
    Никаких фоновых процессов — просто один HTTP POST.
    """
    payload = {"chat_id": TG_CHAT_ID, "text": text}
    r = requests.post(_API, json=payload, timeout=10)
    try:
        data = r.json()
    except Exception:
        r.raise_for_status()
        return
    if r.status_code >= 400 or not data.get("ok", False):
        # Пробрасываем читаемую ошибку Телеги, если есть
        desc = data.get("description") if isinstance(data, dict) else None
        raise RuntimeError(f"Telegram send error {r.status_code}: {desc or data}")

