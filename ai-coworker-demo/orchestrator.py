from prompts import PERSONAS
from retriever import SimpleRetriever
from director import Director
from llm_client import generate_response


class Orchestrator:
    def __init__(self):
        self.retriever = SimpleRetriever()
        self.director = Director()

    def route(self, user_message: str, preferred_agent: str | None = None) -> str:
        if preferred_agent in PERSONAS:
            return preferred_agent

        msg = user_message.lower()
        if any(word in msg for word in ["competency", "talent", "mobility", "360", "coaching"]):
            return "CHRO"
        if any(word in msg for word in ["region", "rollout", "training", "communication", "adoption", "europe"]):
            return "Regional"
        return "CEO"

    def handle_turn(self, user_message: str, recent_turns: list, preferred_agent: str | None = None):
        active_agent = self.route(user_message, preferred_agent)
        persona = PERSONAS[active_agent]
        retrieved = self.retriever.search(user_message, active_agent)
        hint = self.director.inspect(recent_turns, user_message)
        reply = generate_response(persona["persona_prompt"], recent_turns, retrieved, user_message)
        if hint:
            reply += f"\n\nHint: {hint}"
        return {
            "agent": active_agent,
            "reply": reply,
            "retrieved": retrieved,
            "hint": hint,
        }
