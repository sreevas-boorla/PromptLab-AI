# PromptLab AI 🚀
### Enterprise Prompt Engineering, Optimization, Model Comparison & Real Evaluation Platform

PromptLab AI is a full-stack platform built for AI engineers, prompt researchers, and QA teams to design, optimize, benchmark, and evaluate LLM prompts using real mathematical scoring metrics and multi-model side-by-side comparison.

---

## 🌟 Key Features

- **⚡ Prompt Playground**: Interactive editor with system prompt directives, parameter variables (`{{variable_name}}`), temperature sliders, and live latency/token cost telemetry.
- **🪄 Automated Prompt Optimizer**: Transform prompts across 5 strategies (*Chain-of-Thought*, *Few-Shot Framing*, *Role & Persona Directives*, *Token Compression*, *JSON Structuring*) and benchmark original vs. optimized prompts side-by-side under **identical inputs and model settings**.
- **⚔️ Multi-Model Comparison**: Simultaneous execution across GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, and Llama 3 70B with fastest model and lowest cost badges.
- **📊 Real Evaluation Engine**: Automated dataset benchmark runner with 5 non-hardcoded evaluation algorithms:
  1. `ExactMatchEvaluator`: Whitespace and case-insensitive string match.
  2. `RegexMatchEvaluator`: Structural regex pattern verification.
  3. `SemanticSimilarityEvaluator`: 3-gram character TF-IDF cosine similarity & SequenceMatcher ratio.
  4. `JSONSchemaEvaluator`: Strict JSON schema key presence validation.
  5. `LLMAsJudgeEvaluator`: Multi-metric scoring rubric (*Accuracy*, *Relevance*, *Clarity*, *Safety*).
- **📚 Version Controlled Prompt Library**: Immutable revision history (v1, v2, v3) with tagging, search, and category management.
- **📈 Analytics & Telemetry**: Token usage tracking, cost breakdown by model, latency distributions, and evaluation pass rate trends.
- **🔒 Server-Side Key Security**: All external provider API keys remain strictly server-side. Includes fallback deterministic Mock Provider mode.

---

## 🛠️ Architecture & Tech Stack

```
PromptLab AI Architecture
├── Frontend (React + TypeScript + Vite + Tailwind CSS + Lucide Icons + Vitest)
└── Backend  (FastAPI + Python 3.12 + SQLAlchemy + SQLite + Pytest)
```

---

## 🚀 Quickstart Guide

### Prerequisites
- **Node.js** (v18+) & **NPM**
- **Python** (3.10+)

### 1. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
python migrations/migrate.py
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 🧪 Running Automated Tests

### Backend Unit & API Integration Tests
```bash
python -m pytest backend/tests -v
```

### Frontend TypeScript Check & Unit Tests
```bash
cd frontend
npx tsc --noEmit
npm run test
```

### Production Build
```bash
cd frontend
npm run build
```

---

## 📜 License
MIT License. Created for AI Engineering & Benchmark Audit.


## Production security and deployment notes

This application uses a **single-user private workspace** login, not public multi-user accounts. In the backend environment set `PROMPTLAB_ENV=production`, `PROMPTLAB_ACCESS_TOKEN` to a long random passphrase, and `ALLOWED_ORIGINS` to the exact frontend origin. Store all provider API keys as backend-only secrets. Do not put the passphrase in frontend JavaScript or a `VITE_*` variable.

**Important deployment requirement:** Route frontend `/api/v1/*` requests through an HTTPS reverse proxy to the backend under the same site (e.g. your own domain), because the signed HttpOnly session cookie uses SameSite=Lax. Direct cross-site calls from a Vercel domain to a Render domain are not a supported session deployment setup. Configure the proxy and test login, playground and logout before publishing.

Run `python -m pytest backend/tests -v` and `npm run lint && npm run test && npm run build` in `frontend/`. CI performs these checks on pull requests. Mock-provider tests do **not** establish that paid LLM APIs function; use `backend/tests/smoke_test_real_apis.py` with real keys in a secure environment.

Estimated API pricing is hard-coded in `backend/app/providers.py` and may be outdated; treat displayed cost as illustrative until refreshed against provider pricing. Prompt comparisons without reference cases measure evaluator preferences, not verified factual accuracy.
