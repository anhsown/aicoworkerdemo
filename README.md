# AI Co-Worker Engine (Prototype)

This project is a lightweight prototype of an **AI Co-Worker Engine** designed for interactive job simulations.

Instead of a generic chatbot, the system simulates collaboration with AI stakeholders such as a CEO, CHRO, and Regional Manager.

---

## Key Features

- **Multi-agent system**
  - CEO (strategy & brand identity)
  - CHRO (talent & leadership framework)
  - Regional Manager (rollout & adoption)

- **Role-based responses**
  - Each agent responds with a distinct perspective

- **Session memory (basic)**
  - Keeps track of conversation history

- **Director / Supervisor hints**
  - Guides the user when input is vague or repetitive

- **Fallback mode (no API key required)**
  - Rule-based responses that simulate realistic behavior

---

## Design Concepts

| Concept | Implementation |
|--------|--------------|
| NPC agents | `ceo_response`, `chro_response`, `regional_response` |
| Orchestrator | `detect_role()` |
| Director layer | `supervisor_hint()` |
| Memory | in-memory `SESSION` |
| UI | embedded HTML in FastAPI |

---

## Architecture Overview

User → UI → FastAPI → Orchestrator → Agent (CEO / CHRO / Regional)
↓
Supervisor (Hint)
↓
Response


---

## How to Run

### 1. Create virtual environment
- python -m venv .venv
.\.venv\Scripts\activate
### 2. Install dependencies
- pip install fastapi uvicorn
### 3. Run server
- python -m uvicorn main_fixed:app --reload --port 8001
### 4. Open in browser
- http://127.0.0.1:8001
## Demo Examples
- CEO (Strategic thinking)
- We want to standardize leadership across brands. Where do you see the risks?
- CEO (Governance decision)
- Should leadership decisions be centralized or remain at brand level?
- CEO (Innovation vs alignment)
- How do we protect innovation while building alignment?
- CHRO (HR perspective)
- How should we design a competency framework for leadership?
- Regional (Execution)
- How would you roll this out across regions?
- Edge case (Director hint)
- ok
### Why This Matters

- This prototype demonstrates how AI can move from:

- answering questions → simulating real workplace collaboration

- It highlights:

- stakeholder-specific reasoning
- trade-off thinking
guided learning through interaction
### Limitations
- Rule-based fallback (no real LLM yet)
- No persistent database
- No real vector retrieval (RAG is simulated)
### Next Steps
- Integrate OpenAI / LLM API
- Add real RAG (vector DB)
- Improve UI (React + streaming)
- Add evaluation metrics
