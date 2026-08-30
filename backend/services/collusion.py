import json
import math
from itertools import combinations
from config import get_settings
from services.grader import embed_text

settings = get_settings()


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a * norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def compute_tfidf_similarity(text_a: str, text_b: str) -> float:
    if not text_a or not text_b or not text_a.strip() or not text_b.strip():
        return 0.0
    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())
    if not words_a or not words_b:
        return 0.0
    return float(len(words_a & words_b) / max(len(words_a | words_b), 1))


async def detect_collusion(scripts: list[dict], threshold: float) -> list[dict]:
    """
    scripts: list of {script_id, ocr_text, feedbacks: [str]}
    Returns list of flagged pairs above threshold.
    """
    if len(scripts) < 2:
        return []

    # Embed each script's answer
    embeddings = {}
    for s in scripts:
        text = s.get("ocr_text", "")[:4000]
        emb = await embed_text(text)
        embeddings[s["script_id"]] = emb

    flags = []
    for sa, sb in combinations(scripts, 2):
        text_a = sa.get("ocr_text", "")
        text_b = sb.get("ocr_text", "")
        emb_a = embeddings.get(sa["script_id"], [])
        emb_b = embeddings.get(sb["script_id"], [])
        
        if emb_a and emb_b:
            cos_sim = cosine_similarity(emb_a, emb_b)
        else:
            cos_sim = compute_tfidf_similarity(text_a, text_b)

        # Error pattern match: count shared feedback phrases
        fa = set(sa.get("feedbacks", []))
        fb = set(sb.get("feedbacks", []))
        shared = fa & fb
        error_match = len(shared) / max(len(fa | fb), 1) if (fa or fb) else 0.0

        cmi = cos_sim * (0.6 + 0.4 * error_match)

        if cmi >= threshold:
            flags.append({
                "script_a_id": sa["script_id"],
                "script_b_id": sb["script_id"],
                "cmi_score": round(cmi, 4),
                "shared_errors": json.dumps(list(shared)[:5]),
                "matched_phrases": json.dumps([]),
            })

    return flags
