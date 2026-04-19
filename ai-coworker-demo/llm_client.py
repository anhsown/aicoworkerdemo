import os
from typing import List, Dict

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None

from prompts import SYSTEM_INSTRUCTIONS


def build_messages(persona_prompt: str, recent_turns: List[Dict], retrieved_docs: List[Dict], user_message: str):
    retrieval_block = "\n".join(f"- {doc['text']}" for doc in retrieved_docs)
    history_block = "\n".join(
        f"User: {turn['user']}\nAssistant ({turn['agent']}): {turn['assistant']}"
        for turn in recent_turns[-4:]
    )
    developer_prompt = (
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        f"Persona:\n{persona_prompt}\n\n"
        f"Retrieved context:\n{retrieval_block or 'No retrieved context.'}\n\n"
        f"Recent conversation:\n{history_block if history_block else 'No prior turns.'}\n"
    )
    return [
        {"role": "developer", "content": developer_prompt},
        {"role": "user", "content": user_message},
    ]


def _contains_any(text: str, keywords: List[str]) -> bool:
    lower = text.lower()
    return any(keyword in lower for keyword in keywords)


def _extract_previous_assistant_text(recent_turns: List[Dict]) -> str:
    if not recent_turns:
        return ""
    return " ".join(turn.get("assistant", "") for turn in recent_turns[-2:]).strip()


def _make_follow_up(agent: str, user_message: str) -> str:
    if agent == "CEO":
        if _contains_any(user_message, ["risk", "concern"]):
            return "Which risk matters more to you: loss of brand identity, slower execution, or weak adoption?"
        return "Which elements do you believe must be consistent across the group, and which should remain brand-specific?"
    if agent == "CHRO":
        if _contains_any(user_message, ["360", "feedback", "coaching"]):
            return "Would you like to start with the questionnaire design, the rater journey, or the coaching flow?"
        return "Which use case should we design first: recruitment, appraisal, development, or internal mobility?"
    return "Which rollout risk worries you most right now: trainer capability, communication quality, or adoption resistance?"


def _compose_ceo_response(user_message: str, retrieved_text: str, recent_turns: List[Dict]) -> str:
    msg = user_message.lower()
    previous = _extract_previous_assistant_text(recent_turns)

    if _contains_any(msg, ["innovation", "experiment", "creativity"]):
        body = (
            "We protect innovation by aligning on a small number of non-negotiable leadership principles while leaving room for each brand to express them differently. "
            "In a luxury group, over-standardization can suppress the experimentation that keeps each house distinctive. "
            "I would standardize the leadership spine, decision rights, and success metrics, but keep local language, rituals, and behavior examples flexible."
        )
    elif _contains_any(msg, ["centralize", "centralise", "decision-making", "governance"]):
        body = (
            "I would be careful about centralizing too much. Central control can improve speed and consistency, but it can also weaken ownership at the brand level. "
            "For a luxury group, I would centralize only the principles, talent standards, and reporting cadence, while leaving market-facing leadership behavior closer to the brands."
        )
    elif _contains_any(msg, ["risk", "standardize", "standardise", "unified", "one leadership model"]):
        body = (
            "A fully unified model can create consistency, but it also creates strategic risk if it flattens brand identity. "
            "Our brands win because they are distinctive, so the group model should define a common leadership backbone rather than a rigid single style. "
            "That gives us alignment without diluting what makes each house unique."
        )
    elif _contains_any(msg, ["board", "pressure", "faster", "quick results", "move faster"]):
        body = (
            "Under pressure, the temptation is to standardize aggressively, but speed without judgment can damage long-term brand equity. "
            "I would deliver fast by piloting a group-level leadership spine in a few brands first, proving value, and then scaling what works."
        )
    else:
        body = (
            "At group level, I would start by defining the business outcome we want from the leadership system: stronger talent pipelines, more mobility, and clearer leadership expectations. "
            "Then I would decide which elements must be common across the group and which should be tailored by brand."
        )

    if retrieved_text and "brand identity" not in body.lower() and _contains_any(retrieved_text, ["brand identity", "brand dna"]):
        body += " We also need to protect brand DNA, because that is one of the group's core strategic assets."

    if previous and body[:80] in previous:
        body += " I would also ask the leadership team to define clear decision rights so the model supports speed without becoming overly centralized."

    return body + " " + _make_follow_up("CEO", user_message)


def _compose_chro_response(user_message: str, retrieved_text: str, recent_turns: List[Dict]) -> str:
    msg = user_message.lower()

    if _contains_any(msg, ["360", "feedback"]):
        body = (
            "I would design the 360 program around the four core competencies: Vision, Entrepreneurship, Passion, and Trust. "
            "The blueprint should define who rates whom, what anonymity rules apply, how results are debriefed, and how coaching turns feedback into behavior change."
        )
    elif _contains_any(msg, ["coaching", "coach"]):
        body = (
            "The coaching layer should help leaders convert feedback into a few practical habits. "
            "I would use a short cadence, for example an initial debrief followed by two or three coaching sessions focused on goals, behavior experiments, and progress review."
        )
    elif _contains_any(msg, ["competency", "framework", "vision", "entrepreneurship", "passion", "trust"]):
        body = (
            "I would anchor the leadership model in the four competencies of Vision, Entrepreneurship, Passion, and Trust, then describe what each competency looks like at different leadership levels. "
            "That keeps the model simple enough to scale, while still useful for assessment and development."
        )
    elif _contains_any(msg, ["mobility", "talent", "pipeline"]):
        body = (
            "From a talent perspective, the main value of a group-level model is that it creates a common language for identifying and developing leaders across brands. "
            "That makes internal mobility, succession planning, and targeted development much easier."
        )
    else:
        body = (
            "I would start with a shared competency framework and connect it to specific use cases such as recruitment, appraisal, development, and internal mobility. "
            "The model needs to be clear enough for managers to use and flexible enough for brands to adapt."
        )

    if retrieved_text and "vision" in retrieved_text.lower() and "vision" not in body.lower():
        body += " The retrieved simulation context also reinforces that the four competency pillars should stay visible in the final design."

    return body + " " + _make_follow_up("CHRO", user_message)


def _compose_regional_response(user_message: str, retrieved_text: str, recent_turns: List[Dict]) -> str:
    msg = user_message.lower()

    if _contains_any(msg, ["rollout", "launch", "scale"]):
        body = (
            "For rollout, I would avoid a big-bang launch. "
            "A train-the-trainer model is more realistic: pilot in one region or brand, capture resistance points, refine the materials, and then scale with local HR support."
        )
    elif _contains_any(msg, ["training", "trainer", "workshop"]):
        body = (
            "Training should be practical and locally relevant. "
            "I would equip regional trainers with a facilitation guide, role-based examples, a short FAQ, and escalation paths for questions that require group HR support."
        )
    elif _contains_any(msg, ["communication", "comms", "adoption", "resistance"]):
        body = (
            "Adoption usually fails when the message feels imposed from the center. "
            "I would tailor the communication plan by region, explain why the framework matters locally, and give managers simple examples of how it improves decisions and development."
        )
    elif _contains_any(msg, ["kpi", "dashboard", "measure", "measurement"]):
        body = (
            "I would track a mix of leading and lagging indicators, such as workshop attendance, training completion, early manager adoption, mobility movement, and sentiment from regional HR teams. "
            "Those metrics should feed into a simple dashboard reviewed on a regular cadence."
        )
    else:
        body = (
            "At regional level, feasibility matters as much as design quality. "
            "Even a strong framework will fail if local teams do not understand it, trust it, or have the capability to deliver it consistently."
        )

    return body + " " + _make_follow_up("Regional", user_message)


def _fallback_response(persona_prompt: str, user_message: str, retrieved_docs: List[Dict], recent_turns: List[Dict]) -> str:
    retrieved_text = " ".join(doc["text"] for doc in retrieved_docs[:2])
    p = persona_prompt.lower()

    if "ceo" in p:
        return _compose_ceo_response(user_message, retrieved_text, recent_turns)
    if "chro" in p:
        return _compose_chro_response(user_message, retrieved_text, recent_turns)
    return _compose_regional_response(user_message, retrieved_text, recent_turns)


def generate_response(persona_prompt: str, recent_turns: List[Dict], retrieved_docs: List[Dict], user_message: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return _fallback_response(persona_prompt, user_message, retrieved_docs, recent_turns)

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    messages = build_messages(persona_prompt, recent_turns, retrieved_docs, user_message)
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.6,
    )
    return completion.choices[0].message.content.strip()
