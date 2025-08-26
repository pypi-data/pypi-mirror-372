import re
from typing import Dict, List, Iterable
import numpy as np
from ._config import TASK_PAIRS

# --- базовая предобработка ---
_STOP = {"и","в","на","с","по","для","к","от","до","при","как","что","из","за","или","а","но","же","не","о","об","у","это"}
_TOKEN_RE = re.compile(r"[a-zа-яё0-9\^\-\+\*/\.\[\]\(\)=]+", re.IGNORECASE)

def _norm(t: str) -> str:
    t = t.lower().replace("ё", "е")
    t = re.sub(r"[^a-zа-я0-9\^\-\+\*/\.\[\]\(\)=\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

def _tok(t: str) -> List[str]:
    return [w for w in _TOKEN_RE.findall(_norm(t)) if w and w not in _STOP]

def _build_vocab(docs: Iterable[List[str]]) -> Dict[str, int]:
    v = {}
    for toks in docs:
        for w in toks:
            if w not in v:
                v[w] = len(v)
    return v

def _idf(vocab: Dict[str,int], docs: List[List[str]]) -> np.ndarray:
    N = len(docs)
    df = np.zeros(len(vocab), dtype=float)
    for toks in docs:
        for w in set(toks):
            df[vocab[w]] += 1.0
    return np.log((1.0 + N) / (1.0 + df)) + 1.0  # сглажённый IDF

def _tfidf(vocab: Dict[str,int], idf: np.ndarray, toks: List[str]) -> np.ndarray:
    v = np.zeros(len(vocab), dtype=float)
    for w in toks:
        idx = vocab.get(w)
        if idx is not None:
            v[idx] += 1.0
    n = np.linalg.norm(v)
    if n > 0:
        v = (v / n) * idf
    return v

def _cos(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na == 0 or nb == 0 else float(np.dot(a, b) / (na * nb))

def _jacc(a: List[str], b: List[str]) -> float:
    A, B = set(a), set(b)
    u = len(A | B)
    return 0.0 if u == 0 else len(A & B) / u

def _lev_norm(a: str, b: str) -> float:
    a, b = _norm(a), _norm(b)
    m, n = len(a), len(b)
    if m == 0 and n == 0:
        return 1.0
    prev = np.arange(n + 1)
    curr = np.zeros(n + 1, dtype=int)
    for i in range(1, m + 1):
        curr[0] = i
        ai = a[i - 1]
        for j in range(1, n + 1):
            cost = 0 if ai == b[j - 1] else 1
            curr[j] = min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost)
        prev, curr = curr, prev
    dist = prev[n]
    return 1.0 - dist / float(max(m, n))

# --- индекс и глобалы ---
_DOCS = []            # список словарей по документам
_VOCAB: Dict[str,int] = {}
_IDF: np.ndarray | None = None
_INDEX_READY = False

def _build_index():
    global _INDEX_READY, _DOCS, _VOCAB, _IDF
    if _INDEX_READY:
        return
    keys = list(TASK_PAIRS.keys())
    docs_tokens = [_tok(k) for k in keys]
    _VOCAB = _build_vocab(docs_tokens)
    _IDF = _idf(_VOCAB, docs_tokens)

    _DOCS = []
    for k in keys:
        toks = _tok(k)
        vec  = _tfidf(_VOCAB, _IDF, toks)
        nums = {t for t in toks if any(c.isdigit() for c in t)}
        _DOCS.append({
            "key": k,
            "ans": TASK_PAIRS[k],
            "toks": toks,
            "vec": vec,
            "norm": _norm(k),
            "nums": nums
        })
    _INDEX_READY = True

def _query_vec(query: str) -> np.ndarray:
    # используем глобальные VOCAB/IDF; они уже построены
    toks = _tok(query)
    return _tfidf(_VOCAB, _IDF, toks) if _IDF is not None else np.zeros(len(_VOCAB))

def _score(q: str, d, q_vec: np.ndarray, q_toks: List[str], q_norm: str) -> float:
    cos = _cos(q_vec, d["vec"])
    jac = _jacc(q_toks, d["toks"])
    lev = _lev_norm(q_norm, d["norm"])
    q_nums = {t for t in q_toks if any(c.isdigit() for c in t)}
    num_bonus = 0.02 * len(q_nums & d["nums"])
    if num_bonus > 0.10:
        num_bonus = 0.10
    return 0.6 * cos + 0.3 * jac + 0.1 * lev + num_bonus

def find(query: str, top_k: int = 1) -> None:
    """
    Печатает top_k лучших совпадений (key и answer). Ничего не возвращает.
    """
    _build_index()
    q_toks = _tok(query)
    q_norm = _norm(query)
    q_vec  = _query_vec(query)

    scored = []
    for d in _DOCS:
        s = _score(query, d, q_vec, q_toks, q_norm)
        scored.append((d["key"], d["ans"], s))
    scored.sort(key=lambda x: x[2], reverse=True)

    k = max(1, int(top_k))
    for i, (kstr, ans, s) in enumerate(scored[:k], 1):
        print(f"\n=== match #{i} | score={s:.3f} ===")
        print(kstr)
        print(ans)