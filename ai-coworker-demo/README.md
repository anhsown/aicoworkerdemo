# AI Co-Worker Demo

A GitHub-ready prototype for the **AI Co-Worker Engine** take-home assignment.

## What this demo shows

- Multi-agent routing across **CEO**, **CHRO**, and **Regional Manager**
- Mini-RAG from a local simulation knowledge base
- Session memory across turns
- A lightweight **Director** that injects hints when the user is vague or repetitive
- Role-based responses that stay in character
- Optional OpenAI integration via `OPENAI_API_KEY`
- Strong fallback mode that still answers differently for different questions

## Why this version is fixed

The earlier prototype could look repetitive in fallback mode. This version fixes that by:

- answering the **latest user question directly**
- varying fallback behavior by **role + intent + retrieved context**
- reducing repeated phrasing across turns
- keeping debug information out of the UI

## Run locally

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

python -m pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
python -m uvicorn app:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Optional OpenAI setup

Add your API key in `.env`:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Without an API key, the app still works in fallback mode.

## Example prompts

### CEO
- `How do we protect innovation while building alignment?`
- `Should leadership decisions be centralized or stay at brand level?`

### CHRO
- `How would you design the 360 feedback and coaching program?`
- `How should we structure the competency model?`

### Regional Manager
- `How would you roll this out across regions?`
- `Which KPIs should we track during adoption?`
