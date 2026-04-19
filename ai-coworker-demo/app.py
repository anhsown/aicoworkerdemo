from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI()

SESSION = {"history": []}

class ChatRequest(BaseModel):
    message: str
    role: str = "auto"

def detect_role(user_msg: str, selected_role: str) -> str:
    if selected_role in {"ceo", "chro", "regional"}:
        return selected_role
    text = user_msg.lower()
    if any(k in text for k in ["competency", "talent", "mobility", "360", "coaching", "framework"]):
        return "chro"
    if any(k in text for k in ["rollout", "region", "training", "adoption", "communication", "local"]):
        return "regional"
    return "ceo"

def supervisor_hint(user_msg: str):
    text = user_msg.strip().lower()
    if len(text.split()) <= 3:
        return "Try being more specific about the trade-off or outcome you want."
    return None

def ceo_response(user_msg: str) -> str:
    text = user_msg.lower()

    if "innovation" in text and "alignment" in text:
        return (
            "Protecting innovation while building alignment requires a clear boundary between shared principles and local freedom. "
            "At group level, I would align on a small leadership spine such as accountability, collaboration, and decision quality. "
            "But I would not force every brand to express leadership in the same way. In luxury, innovation often depends on brand-specific identity. "
            "So the real question is: which capabilities must be common across the group, and where should brands keep room to experiment?"
        )

    if "centralized" in text or "centralised" in text or "brand level" in text:
        return (
            "I would avoid fully centralizing leadership decisions. We need some group-level consistency, but luxury brands also need autonomy to protect "
            "their identity and creative energy. I would use a hybrid model: define core principles centrally, while letting brands decide how those principles "
            "are applied in practice. The important question is which decisions benefit from central governance and which should stay close to the brand."
        )

    if "standardize" in text or "standardise" in text or "unified" in text:
        return (
            "I understand the desire for consistency, but a fully unified leadership model across all brands can be risky. Brand identity is one of our biggest "
            "strategic assets, and over-standardization can flatten what makes each house distinctive. I would define a small group-level leadership spine first, "
            "then allow each brand to express it in its own language and behaviors. Which elements do you believe must be consistent across the group, and which "
            "should remain brand-specific?"
        )

    if "pressure" in text or "board" in text or "move faster" in text:
        return (
            "Speed matters, but moving faster by over-centralizing can create longer-term damage. In a luxury portfolio, the wrong kind of consistency can weaken "
            "differentiation. I would rather move in phases: first define the non-negotiable principles, then pilot the model with a few brands, and only scale what works."
        )

    return (
        "From a CEO perspective, I would first clarify the strategic trade-off. The issue is not only consistency, but how to strengthen group leadership without weakening "
        "the identity of each brand. Before choosing a solution, I would ask what business outcome you are optimizing for: stronger mobility, better succession, faster capability building, "
        "or tighter cultural alignment."
    )

def chro_response(user_msg: str) -> str:
    text = user_msg.lower()

    if "360" in text or "feedback" in text or "coaching" in text:
        return (
            "From a CHRO perspective, I would design the 360 and coaching program around the shared competency framework, not as a generic feedback exercise. "
            "That means defining rater groups, anonymity rules, language coverage, and coaching goals that connect directly to leadership development."
        )

    if "mobility" in text or "talent" in text:
        return (
            "Inter-brand mobility works only if leaders are assessed through a shared language of potential and performance. I would recommend a competency framework "
            "that is consistent at group level but flexible in local expression."
        )

    if "competency" in text or "framework" in text:
        return (
            "I would structure the leadership framework around a small number of common themes such as Vision, Entrepreneurship, Passion, and Trust. "
            "Each theme should have behavior indicators by level so it can support recruitment, appraisal, development, and mobility."
        )

    return (
        "My priority as CHRO would be to make the model usable across the talent lifecycle: selection, development, succession, and mobility. "
        "If the design is too abstract, managers will ignore it. If it is too rigid, brands will resist it."
    )

def regional_response(user_msg: str) -> str:
    text = user_msg.lower()

    if "rollout" in text or "region" in text:
        return (
            "From a regional perspective, rollout success depends less on the framework itself and more on how it is introduced. Local teams need clear communication, "
            "practical training, and enough flexibility to adapt the materials to market realities."
        )

    if "training" in text or "adoption" in text or "communication" in text:
        return (
            "The biggest adoption risk is that local teams see this as another top-down HR initiative. To avoid that, I would tailor the communication to each market, "
            "explain why the model matters, and provide practical examples managers can use immediately."
        )

    return (
        "At regional level, the main questions are feasibility, readiness, and local relevance. Even a strong group design can fail if it creates too much complexity "
        "for local teams or if the communication does not explain how the framework supports day-to-day management."
    )

def generate_response(role: str, user_msg: str) -> str:
    if role == "ceo":
        reply = ceo_response(user_msg)
    elif role == "chro":
        reply = chro_response(user_msg)
    else:
        reply = regional_response(user_msg)

    hint = supervisor_hint(user_msg)
    if hint:
        reply += f"\n\nHint: {hint}"
    return reply

@app.post("/chat")
async def chat(req: ChatRequest):
    role = detect_role(req.message, req.role)
    reply = generate_response(role, req.message)

    SESSION["history"].append({
        "role": role,
        "user": req.message,
        "assistant": reply
    })

    print("ROLE:", role)
    print("USER:", req.message)
    print("REPLY:", reply[:120], "...")
    print("-" * 50)

    return JSONResponse({"role": role.upper(), "reply": reply})

@app.post("/reset")
async def reset():
    SESSION["history"] = []
    return {"ok": True}

HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>AI Co-Worker Demo</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f6f7fb; margin: 0; }
    .wrap { max-width: 1100px; margin: 24px auto; background: white; padding: 24px; border-radius: 18px; }
    h1 { margin: 0 0 8px 0; }
    .sub { color: #666; margin-bottom: 18px; }
    .row { display: flex; gap: 12px; margin-bottom: 16px; }
    select, button, textarea { font-size: 16px; border-radius: 12px; border: 1px solid #cfd6e4; }
    select, button { padding: 12px 16px; }
    button.primary { background: #0d1b3e; color: white; border: none; }
    textarea { width: 100%; min-height: 120px; padding: 16px; resize: vertical; box-sizing: border-box; }
    .chat { margin-top: 20px; display: flex; flex-direction: column; gap: 16px; }
    .bubble { padding: 18px; border-radius: 18px; line-height: 1.55; white-space: pre-wrap; }
    .ai { background: #f1f1f4; }
    .user { background: #dfe9ff; }
    .label { font-weight: bold; color: #5b6574; margin-bottom: 8px; font-size: 14px; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>AI Co-Worker Demo</h1>
    <div class="sub">Role-based replies with clean fallback behavior.</div>

    <div class="row">
      <select id="role">
        <option value="ceo">CEO</option>
        <option value="chro">CHRO</option>
        <option value="regional">Regional</option>
        <option value="auto">Auto</option>
      </select>
      <button class="primary" onclick="sendMsg()">Send</button>
      <button onclick="resetChat()">Reset session</button>
    </div>

    <textarea id="msg" placeholder="Ask a question..."></textarea>
    <div class="chat" id="chat"></div>
  </div>

<script>
async function sendMsg() {
  const msgEl = document.getElementById("msg");
  const roleEl = document.getElementById("role");
  const chatEl = document.getElementById("chat");
  const message = msgEl.value.trim();
  if (!message) return;

  chatEl.innerHTML += `
    <div class="bubble user">
      <div class="label">You</div>
      ${escapeHtml(message)}
    </div>
  `;

  const res = await fetch("/chat", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({message, role: roleEl.value})
  });

  const data = await res.json();

  chatEl.innerHTML += `
    <div class="bubble ai">
      <div class="label">AI (${data.role})</div>
      ${escapeHtml(data.reply)}
    </div>
  `;

  msgEl.value = "";
}

async function resetChat() {
  await fetch("/reset", { method: "POST" });
  document.getElementById("chat").innerHTML = "";
}

function escapeHtml(text) {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;")
    .replaceAll("\\n", "<br>");
}
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return HTML