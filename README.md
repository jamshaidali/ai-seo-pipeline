# AI Visibility Intelligence API

A RESTful Flask API with an AI-powered multi-agent backend that discovers high-value SEO queries, scores their opportunity, and recommends content.

## Architecture Decisions

- **Flask App Factory Pattern:** Decoupled extensions and configuration for better testability and modularity.
- **Agent Separation:** Three autonomous agents inheriting from `BaseAgent`, which encapsulates LLM call structure using OpenAI's `beta.chat.completions.parse` method and Pydantic for rigid JSON adherence.
- **Synchronous Execution:** A simplified, robust synchronous orchestrator pattern. Partial failures are resilient (e.g. if one query scoring fails, it continues processing the rest).
- **SQLite Database:** Used for rapid deployment, easily swappable for Postgres in production. ORM driven by SQLAlchemy.
- **Pydantic Validation:** Ensures only valid schemas are saved or sent.

## Opportunity Score Formula

The opportunity score is a scalar in the range `[0.0, 1.0]`. It consists of four weighted components:
1. **Search Volume (30%)**: Normalized by capping typical high volume at 10,000 to keep it manageable.
2. **Competitive Difficulty (30%)**: Scaled inversely. `(100 - Diff) / 100`. Easier queries yield high scores.
3. **Visibility Gap (30%)**: `1.0` if target domain is not visible, `0.0` otherwise. High penalty for currently ranking.
4. **Commercial Intent (10%)**: Flat `0.1` bonus if query contains comparison keywords ('vs', 'best', 'review', 'alternative').

Formula:
`Score = (0.3 * VolNorm) + (0.3 * DiffNorm) + (0.3 * Gap) + (0.1 * Intent)`

## Setup & Running

**Using pure Python**
```bash
python -m venv .venv
# Activate your venv
pip install -r requirements.txt
cp .env.example .env
# Edit .env and supply OPENAI_API_KEY
flask db init
flask db migrate -m \"init\"
flask db upgrade
python run.py
```

**Using Docker**
```bash
cp .env.example .env
# Make sure OPENAI_API_KEY is placed in .env
docker-compose up --build
```
