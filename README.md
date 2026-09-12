NourishAI Pakistan

AI-powered personalized meal planning for Pakistani users, built with Streamlit and Groq.

NourishAI Pakistan is a hackathon-focused nutrition planning application that turns a user's goals, dietary preferences, allergies, health considerations, cuisine preferences, and budget into a practical personalized meal plan.

The current application extends the original MVP with account authentication, saved-plan history, professional document export, fitness/gym context, and a broader universal planning model while retaining the original Pakistan-first product direction.

Product

Core experience

Create an account or sign in.

Enter personal context and planning preferences.

Select goals, dietary requirements, allergies, health considerations, cuisines, fitness context, and budget.

Generate an AI-personalized meal plan.

Save the plan to personal history.

Download the plan as a professional Word document.

Revisit or delete saved plans from the user's own history.

Key capabilities

Personalized meal planning

Pakistan-friendly food recommendations

Goal-aware planning: lose, maintain, gain, muscle building, strength/performance, and healthier eating

Dietary-requirement handling

Strict allergy exclusions

Health-consideration-aware recommendations

Cuisine and food-culture preferences

Budget-aware planning

Fitness and gym context

Recipe search resources

User accounts and sign-in/sign-out

Password reset/change flows

Per-user saved-plan history

Professional .docx export

Responsive Streamlit interface

Groq-powered structured AI generation

Technology

Frontend: Streamlit

Language: Python

AI: Groq API using the OpenAI-compatible endpoint

Default model: openai/gpt-oss-20b

Persistence: SQLite for the hackathon MVP

Document export: python-docx

Version control: Git / GitHub

Repository

Recommended GitHub repository:

nourishai-pakistan

Project structure

nourishai-pakistan/
├── app/
│   ├── main.py
│   ├── catalog.py
│   └── storage.py
├── data/
│   └── nourishai.db          # generated locally; do not commit
├── docs/
├── .streamlit/
├── .env                      # local only; do not commit
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

Local setup

1. Create a virtual environment

Windows:

python -m venv .venv
.venv\Scripts\activate

macOS/Linux:

python3 -m venv .venv
source .venv/bin/activate

2. Install dependencies

pip install -r requirements.txt

3. Configure environment variables

Create .env in the project root:

GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b

Never commit .env or any API key to GitHub.

4. Run the application

streamlit run app/main.py

Open:

http://localhost:8501

Git workflow

The project uses two primary branches:

main  -> stable / submission-ready
dev   -> active development

Recommended workflow:

git checkout dev
# make changes
git add .
git commit -m "feat: describe the change"
git push origin dev

After testing:

git checkout main
git merge dev
git push origin main

Safety and responsible-use boundaries

NourishAI is a general wellness and meal-planning application. It is not a medical diagnostic or treatment system.

The application must not:

Diagnose medical conditions

Prescribe medication

Claim to treat or cure disease

Guarantee health outcomes

Present the plan as a replacement for professional medical or nutritional advice

Recommend a stated allergen

Invent or claim unverified Halal/Kosher certification

Health conditions are used as user-provided dietary considerations with cautious language.

Allergies are treated as strict exclusions.

Important product scope

The original PRD defines a Pakistan-focused Streamlit MVP centered on a personalized 7-day meal plan. The current implementation adds product extensions such as accounts, saved history, document export, and fitness context.

Where the current implementation extends the original PRD, those capabilities should be described as post-MVP extensions, not as claims that they were part of the original PRD.

Hackathon deliverables

The project is designed to support:

Public deployment link

Public GitHub repository

PRD / product documentation

Presentation slides

4–5 minute demonstration video

Status

Hackathon MVP — active development on dev

The priority is a reliable end-to-end flow:

Collect
  ↓
Validate
  ↓
Understand
  ↓
Personalize
  ↓
Generate
  ↓
Display
  ↓
Save / Download

Disclaimer

This application is for general informational and meal-planning purposes only. It is not a substitute for professional medical or nutritional advice. Users with medical conditions should consult a qualified healthcare professional before making significant dietary changes.