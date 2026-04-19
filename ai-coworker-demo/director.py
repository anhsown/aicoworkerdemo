from typing import List, Dict, Optional

class Director:
    def inspect(self, recent_turns: List[Dict], user_message: str) -> Optional[str]:
        msg = user_message.strip()
        if len(msg.split()) < 4:
            return "Try being more specific about the business problem, stakeholder concern, or deliverable you want help with."

        if len(recent_turns) >= 2:
            last_user_msgs = [t["user"].strip().lower() for t in recent_turns[-2:]]
            if all(last == msg.lower() for last in last_user_msgs):
                return "You may be repeating yourself. Try reframing the question around trade-offs, risks, or next steps."

        return None
