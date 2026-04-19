import json
import re
from pathlib import Path
from typing import List, Dict

KB_PATH = Path(__file__).parent / "data" / "knowledge_base.json"


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9\-]+", text.lower()))


class SimpleRetriever:
    def __init__(self, kb_path: Path = KB_PATH):
        self.docs = json.loads(kb_path.read_text(encoding="utf-8"))

    def search(self, query: str, active_agent: str, top_k: int = 3) -> List[Dict]:
        query_terms = _tokenize(query)
        agent_terms = _tokenize(active_agent)
        scored = []
        for doc in self.docs:
            tags = _tokenize(" ".join(doc.get("tags", [])))
            text_terms = _tokenize(doc["text"])
            overlap = len(query_terms & tags) * 3 + len(query_terms & text_terms)
            overlap += len(agent_terms & tags) * 2
            if query_terms & {"360", "feedback", "coaching"} and "360" in tags:
                overlap += 4
            if query_terms & {"kpi", "measurement", "dashboard"} and "kpi" in tags:
                overlap += 4
            scored.append((overlap, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        hits = [doc for score, doc in scored[:top_k] if score > 0]
        if hits:
            return hits
        fallback = next((doc for doc in self.docs if active_agent.lower() in " ".join(doc.get("tags", [])).lower()), None)
        return [fallback] if fallback else [self.docs[0]]
