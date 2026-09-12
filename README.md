<div align="center">

# 🥗 NourishAI Pakistan

### AI-Powered Personalized Nutrition & Meal Planning

**A universal nutrition studio with a Pakistan-first origin — personalized around your goals, food culture, dietary requirements, allergies, fitness context, health considerations, and budget.**

<p>
  <img src="https://img.shields.io/badge/Platform-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/AI-Groq-111827?style=for-the-badge" alt="Groq">
  <img src="https://img.shields.io/badge/Status-Hackathon%20MVP-0F766E?style=for-the-badge" alt="Hackathon MVP">
</p>

<p>
  <a href="#-features">Features</a> •
  <a href="#-product-flow">Product Flow</a> •
  <a href="#-technology">Technology</a> •
  <a href="#-local-setup">Setup</a> •
  <a href="#-project-structure">Structure</a> •
  <a href="#-safety">Safety</a>
</p>

</div>

---

## 🎯 What is NourishAI?

**NourishAI Pakistan** is a Streamlit-based AI nutrition planning application designed to turn a user's personal context into a practical meal plan.

The original product was designed around the Pakistani market and a 7-day personalized meal-planning experience. The current implementation extends that foundation with:

- User accounts
- Saved-plan history
- Professional Word document export
- Fitness and gym context
- Broader global food and dietary context
- Multiple planning periods
- Multiple currencies and budgets

The goal is simple:

> **Collect the right context → understand the constraints → personalize the plan → generate practical meals → let the user save and revisit the result.**

---

## ✨ Core Features

### 🧠 AI-Personalized Planning
Generate meal plans from:

- Personal profile
- Primary goal
- Current and target weight
- Activity level
- Fitness / gym context
- Dietary requirements
- Food allergies
- Health considerations
- Faith / food-practice preferences
- Preferred cuisines
- Foods the user likes / avoids
- Budget and planning cadence
- Meal variety preferences

### 🌍 Global Food Context
The application supports country/region-aware planning, cuisine regions, country-inspired cuisines, currencies, and different dietary or food-practice preferences.

### 🛡️ Constraint-First Nutrition
Declared allergies are treated as **strict exclusions**. Dietary requirements and health considerations are carried through the AI generation workflow.

### 🏋️ Fitness-Aware Planning
The planner can account for goals and contexts such as:

- Weight loss
- Weight gain
- Weight maintenance
- Muscle building
- Strength / performance
- Endurance
- Body recomposition
- General healthy eating
- Activity level
- Training type
- Workout timing

### 👤 Accounts & Personal History
Users can:

- Register
- Sign in
- Sign out
- Reset / change passwords
- Save plans
- Reopen previous plans
- Delete saved plans

Each user's saved history is separated by account.

### 📄 Professional Plan Export
Generated plans can be exported as a professional `.docx` document for offline use and sharing.

### 🍽️ Practical Recipe Resources
Meals can include recipe search resources. The application avoids inventing unverified recipe/video URLs.

---

## 🧭 Product Flow

```text
┌──────────────────────┐
│  Create account /    │
│      Sign in         │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│   Personal context   │
│ Goal • Profile       │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Food & culture       │
│ Diet • Allergies     │
│ Cuisine • Preferences│
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Health & fitness     │
│ Activity • Training  │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Budget & planning    │
│ Cadence • Variety    │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│     Groq AI          │
│ Constraint-aware     │
│ structured generation│
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Personalized plan   │
│ Meals • Recipes      │
└───────┬────────┬─────┘
        ↓        ↓
   Save history  Download
                  DOCX
```

---

## 📅 Planning Periods

NourishAI supports different generation scopes instead of assuming every user wants a weekly plan:

| Planning scope | Intended output |
|---|---|
| **Per meal** | One personalized meal |
| **Per day** | One personalized day |
| **Per week** | Seven-day plan |
| **Per month** | Four-week / 28-day planning cycle |

Budget cadence is handled separately so planning duration and budget duration are not confused.

---

## 💡 Original PRD vs Current Product

The original PRD defined a **Pakistan-focused Streamlit MVP** centered on collecting profile, goals, dietary constraints, allergies, health considerations, cuisines, and PKR budget, then generating a personalized 7-day meal plan with recipe resources.

The current implementation extends that MVP with product features that were **not part of the original PRD**, including:

- Authentication
- Saved plan history
- Word export
- Fitness / gym context
- Global country and currency support
- Broader dietary and food-practice options
- Multiple planning periods

This distinction is intentional so the project documentation remains accurate.

---

## 🛠️ Technology

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Language | Python |
| AI | Groq API |
| AI Integration | OpenAI-compatible API endpoint |
| Default AI Model | `openai/gpt-oss-20b` |
| Persistence | SQLite |
| Document Export | `python-docx` |
| Configuration | `.env` |
| Version Control | Git / GitHub |

---

## 📁 Project Structure

```text
nourishai-pakistan/
│
├── app/
│   ├── main.py
│   ├── catalog.py
│   └── storage.py
│
├── data/
│   └── nourishai.db          # generated locally; do NOT commit
│
├── docs/
│   ├── PRD-reference.md
│   └── ...
│
├── .streamlit/
│
├── .env                      # local secrets; do NOT commit
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Calipha-Rayyan/NourishAI-Pakistan.git
cd NourishAI-Pakistan
```

### 2. Create a virtual environment

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

> **Never commit `.env` or expose your API key in the repository.**

### 5. Run the application

```bash
streamlit run app/main.py
```

Open:

```text
http://localhost:8501
```

---

## 🌿 Git Branch Strategy

The repository uses:

```text
main  → stable / submission-ready
dev   → active development
```

Recommended workflow:

```bash
git checkout dev
git add .
git commit -m "feat: describe the change"
git push origin dev
```

After testing and approval:

```bash
git checkout main
git merge dev
git push origin main
```

---

## 🔐 Safety & Responsible Use

NourishAI is a **general wellness and meal-planning application**. It is not a medical diagnosis or treatment system.

The application should **not**:

- Diagnose medical conditions
- Prescribe medication
- Claim to treat or cure disease
- Guarantee health outcomes
- Replace a qualified doctor or dietitian
- Recommend a declared allergen
- Claim religious certification that cannot be verified

Health conditions are treated as user-provided dietary considerations with cautious language.

Allergies are treated as strict exclusions.

Budget recommendations are estimates rather than live market prices.

---

## 🏆 Hackathon Deliverables

The project is designed to support the required submission package:

- ✅ Working deployment
- ✅ Public GitHub repository
- ✅ Product Requirements Document
- ✅ Presentation slides
- ✅ 4–5 minute product demonstration video

The main demonstration story is:

```text
Problem
  ↓
User context
  ↓
AI personalization
  ↓
Working meal plan
  ↓
Save / Download
  ↓
Real-world value
```

---

## 📌 Current Status

**Hackathon MVP — Active Development**

Current focus:

1. Reliable AI generation
2. Strong constraint handling
3. Professional responsive UX
4. Account and history reliability
5. Save / download workflow
6. Stable deployment
7. Submission readiness

---

## 📄 Documentation

- [Product Requirements Reference](PRD-reference.md)
- [Application source](app/)
- [Project dependencies](requirements.txt)

---

## ⚠️ Disclaimer

NourishAI is provided for general informational and meal-planning purposes only. It is not a substitute for professional medical or nutritional advice. Users with medical conditions should consult a qualified healthcare professional before making significant dietary changes.

---

<div align="center">

### 🥗 NourishAI Pakistan

**Personalized planning. Practical food. Smarter choices.**

Built for the hackathon • Streamlit • Python • Groq

</div>
