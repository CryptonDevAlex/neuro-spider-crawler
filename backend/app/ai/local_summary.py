import re
from collections import Counter

from app.ai.schemas import ExecutiveSummary
from app.models.crawl import KeyPoint

STOPWORDS = {
    "de", "la", "el", "los", "las", "un", "una", "que", "para", "con", "por", "del",
    "the", "and", "for", "with", "from", "this", "that", "into", "your", "you", "are",
    "sobre", "como", "más", "mas", "sus", "web", "http", "https",
    "www", "com", "net", "org", "bio", "nav",
}


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [part.strip() for part in parts if len(part.strip()) > 30][:200]


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-záéíóúñ]{4,}", text.lower())


def local_summary(pages: list[dict[str, object]]) -> ExecutiveSummary:
    corpus = " ".join(str(page.get("text") or "") for page in pages)[:30000]
    sentences = _sentences(corpus)
    frequencies = Counter(token for token in _tokens(corpus) if token not in STOPWORDS)

    scored = []
    for index, sentence in enumerate(sentences):
        score = sum(frequencies.get(token, 0) for token in _tokens(sentence))
        scored.append((score, index, sentence))

    top = sorted(scored, key=lambda item: item[0], reverse=True)[:5]
    top.sort(key=lambda item: item[1])

    key_points = [
        KeyPoint(text=sentence[:220], weight=float(score))
        for score, _, sentence in top
    ]
    executive_summary = " ".join(sentence[:300] for _, _, sentence in top[:3])
    titles = [str(page.get("title") or "") for page in pages if page.get("title")]
    entities = list(dict.fromkeys(titles))[:8]

    return ExecutiveSummary(
        executive_summary=executive_summary[:1200] or "No se extrajo texto suficiente.",
        key_points=key_points or [KeyPoint(text="Sin puntos clave disponibles")],
        entities=entities,
    )
