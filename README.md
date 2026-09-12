# NourishAI Pakistan

AI-powered personalized meal planning for Pakistani users.

## Repository
**Recommended GitHub repository name:** `nourishai-pakistan`

## What it does
NourishAI Pakistan generates a practical, culturally relevant 7-day meal plan from a user's goals, dietary preferences, allergies, health considerations, preferred cuisines, and PKR budget.

## Stack
- Streamlit
- Python
- Groq API (OpenAI-compatible endpoint)
- GitHub

## Run locally
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

Then:
```bash
streamlit run app/main.py
```

## Safety
This app is for general informational and meal-planning purposes. It does not diagnose conditions, prescribe treatment or medication, or replace a doctor or dietitian. Allergies are treated as strict exclusions in the AI prompt.
