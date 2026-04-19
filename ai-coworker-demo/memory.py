from collections import defaultdict
from typing import List, Dict

class SessionMemory:
    def __init__(self):
        self._store = defaultdict(list)

    def add_turn(self, session_id: str, user_message: str, assistant_message: str, active_agent: str):
        self._store[session_id].append({
            "user": user_message,
            "assistant": assistant_message,
            "agent": active_agent,
        })

    def recent(self, session_id: str, limit: int = 6) -> List[Dict]:
        return self._store[session_id][-limit:]

    def clear(self, session_id: str):
        self._store[session_id] = []
