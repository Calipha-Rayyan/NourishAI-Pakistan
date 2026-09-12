from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote_plus

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

APP_NAME = "NourishAI Pakistan"
TAGLINE = "Personalized meal planning, grounded in Pakistani food culture."
DISCLAIMER = (
    "This meal plan is for general informational purposes and is not a substitute for "
    "professional medical or nutritional advice. If you have a medical condition, "
    "consult a qualified healthcare professional before making significant dietary changes."
)

st.set_page_config(
    page_title=f"{APP_NAME} · Personalized Meal Planner",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Styling ----------
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
      :root { --ink:#173A35; --teal:#0F766E; --teal2:#115E59; --mint:#E8F5F1; --cream:#FFFDF8; --line:#D8E5E1; --muted:#5C726D; }
      html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
      .stApp { background: linear-gradient(180deg, #F7FAF8 0%, #FFFFFF 55%, #FBFDFC 100%); color:var(--ink); }
      .block-container { max-width: 1200px; padding-top: 1.5rem; padding-bottom: 3rem; }
      .hero { background: radial-gradient(circle at 85% 15%, rgba(255,255,255,.8), transparent 26%), linear-gradient(135deg,#0F766E 0%,#115E59 48%,#173A35 100%); border-radius: 28px; padding: 2.4rem 2.6rem; color:#fff; box-shadow:0 18px 50px rgba(23,58,53,.16); overflow:hidden; position:relative; }
      .hero:after { content:'🥬'; position:absolute; right:7%; top:15%; font-size:7rem; opacity:.14; transform:rotate(-12deg); }
      .eyebrow { letter-spacing:.14em; text-transform:uppercase; font-size:.74rem; font-weight:700; opacity:.85; }
      .hero h1 { font-family:'Playfair Display',serif; font-size:3.1rem; line-height:1.02; margin:.5rem 0 .7rem; }
      .hero p { font-size:1.05rem; max-width:720px; line-height:1.7; opacity:.92; margin:0; }
      .pill { display:inline-flex; align-items:center; gap:.45rem; background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.2); padding:.45rem .75rem; border-radius:999px; font-size:.82rem; margin-top:1rem; }
      .section-title { font-family:'Playfair Display',serif; font-size:1.65rem; color:var(--ink); margin:1.3rem 0 .35rem; }
      .section-sub { color:var(--muted); margin:0 0 .9rem; }
      .card { background:#fff; border:1px solid var(--line); border-radius:20px; padding:1.2rem 1.25rem; box-shadow:0 8px 25px rgba(23,58,53,.05); height:100%; }
      .stat { background:var(--mint); border-radius:16px; padding:1rem 1.1rem; text-align:center; }
      .stat .big { font-size:1.5rem; font-weight:700; color:var(--teal2); }
      .stat .small { color:var(--muted); font-size:.8rem; margin-top:.2rem; }
      .meal-card { background:#fff; border:1px solid var(--line); border-radius:18px; padding:1rem 1.1rem; margin-bottom:.85rem; box-shadow:0 7px 20px rgba(23,58,53,.04); }
      .meal-type { color:var(--teal); font-size:.72rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; }
      .meal-name { font-size:1.04rem; font-weight:700; color:var(--ink); margin:.15rem 0 .3rem; }
      .meal-desc { color:#49625D; font-size:.9rem; line-height:1.55; }
      .tag { display:inline-block; font-size:.72rem; background:#EFF7F4; color:var(--teal2); border-radius:999px; padding:.28rem .55rem; margin:.2rem .2rem 0 0; border:1px solid #DCEDE8; }
      .warning { background:#FFF8E8; border:1px solid #F1DCA0; color:#6B5622; border-radius:14px; padding:.85rem 1rem; font-size:.88rem; line-height:1.5; }
      .footer { color:#6A7D78; font-size:.78rem; text-align:center; padding-top:2rem; }
      div[data-testid="stForm"] { border:0; padding:0; }
      .stButton > button { border-radius:12px; border:1px solid var(--line); font-weight:600; }
      .stButton > button[kind="primary"] { background:var(--teal); color:#fff; border:0; box-shadow:0 8px 18px rgba(15,118,110,.18); }
      .stProgress > div > div { background:var(--teal); }
      .small-note { color:var(--muted); font-size:.8rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_secret(key: str) -> str | None:
    value = os.getenv(key)
    if value:
        return value
    try:
        value = st.secrets.get(key)
    except Exception:
        value = None
    return value


def youtube_search_url(meal_name: str) -> str:
    return f"https://www.youtube.com/results?search_query={quote_plus(meal_name + ' recipe')}"


def normalize_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str):
        return [x.strip() for x in re.split(r",|\n", value) if x.strip()]
    return [str(value).strip()]


def build_prompt(data: dict[str, Any]) -> str:
    return f"""
You are a cautious nutrition-planning assistant for a Pakistani meal-planning web app.
Generate a structured 7-day meal plan from the user's constraints.

USER PROFILE
Age: {data['age']}
Gender: {data['gender']}
Weight: {data['weight']} {data['weight_unit']}
Height: {data['height']} {data['height_unit']}
Goal: {data['goal']}
Allergies (STRICT EXCLUSIONS): {', '.join(data['allergies']) or 'None stated'}
Dietary restrictions: {', '.join(data['restrictions']) or 'None stated'}
Health conditions / considerations: {', '.join(data['health_conditions']) or 'None stated'}
Preferred cuisines: {', '.join(data['cuisines']) or 'Pakistani'}
Budget: PKR {data['budget_amount']} {data['budget_frequency']}
Dietary requirement: Halal by default; do not make unverified Halal-certification claims.
Plan duration: 7 days

HARD RULES
1. Never include an explicitly stated allergen, including in optional garnishes or sauces.
2. Respect dietary restrictions on every day and meal.
3. Treat health conditions only as dietary considerations. Do not diagnose, prescribe medication, or claim to treat/cure disease.
4. Keep recommendations practical, culturally relevant, affordable, and commonly available in Pakistan.
5. Use Pakistani food terminology where appropriate.
6. Avoid unnecessary repetition across the 7 days.
7. For budget, provide a qualitative budget fit label (within budget / near budget / may exceed) rather than fake exact pricing.
8. Do not invent specific YouTube video URLs or claim verified Halal certification. Return recipe_search terms only, and the app will safely create YouTube search links.
9. Use cautious language for medical considerations.
10. Return valid JSON only. No markdown.

OUTPUT JSON SCHEMA
{{
  "summary": "2-3 sentence explanation of how the plan was personalized",
  "days": [
    {{
      "day": 1,
      "budget_fit": "within budget",
      "meals": [
        {{
          "type": "Breakfast",
          "name": "Meal name",
          "description": "Short practical description",
          "dietary_considerations": ["..."],
          "recipe_search": "Meal name Pakistan recipe"
        }},
        {{
          "type": "Lunch",
          "name": "Meal name",
          "description": "Short practical description",
          "dietary_considerations": ["..."],
          "recipe_search": "..."
        }},
        {{
          "type": "Dinner",
          "name": "Meal name",
          "description": "Short practical description",
          "dietary_considerations": ["..."],
          "recipe_search": "..."
        }},
        {{
          "type": "Snack",
          "name": "Optional snack",
          "description": "Short practical description",
          "dietary_considerations": ["..."],
          "recipe_search": "..."
        }}
      ]
    }}
  ]
}}
""".strip()


MEAL_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "days": {
            "type": "array",
            "minItems": 7,
            "maxItems": 7,
            "items": {
                "type": "object",
                "properties": {
                    "day": {"type": "integer"},
                    "budget_fit": {
                        "type": "string",
                        "enum": ["within budget", "near budget", "may exceed"],
                    },
                    "meals": {
                        "type": "array",
                        "minItems": 3,
                        "maxItems": 4,
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": ["Breakfast", "Lunch", "Dinner", "Snack"],
                                },
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "dietary_considerations": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "recipe_search": {"type": "string"},
                            },
                            "required": [
                                "type",
                                "name",
                                "description",
                                "dietary_considerations",
                                "recipe_search",
                            ],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["day", "budget_fit", "meals"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["summary", "days"],
    "additionalProperties": False,
}


def generate_plan(data: dict[str, Any]) -> dict[str, Any]:
    api_key = get_secret("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. Add it to .env or Streamlit secrets."
        )

    model = get_secret("GROQ_MODEL") or "openai/gpt-oss-20b"
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    response = client.chat.completions.create(
        model=model,
        temperature=0.55,
        max_completion_tokens=8000,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "nourishai_weekly_meal_plan",
                "strict": True,
                "schema": MEAL_PLAN_SCHEMA,
            },
        },
        messages=[
            {
                "role": "user",
                "content": (
                    build_prompt(data)
                    + "\n\nReturn ONLY the JSON object matching the supplied response schema. "
                    + "Do not include Markdown, explanations outside the JSON, or extra fields."
                ),
            }
        ],
    )

    content = response.choices[0].message.content or ""
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "The AI returned an unreadable meal plan. Please try again."
        ) from exc

    if not isinstance(parsed, dict) or not isinstance(parsed.get("days"), list):
        raise ValueError("The AI returned an incomplete meal plan. Please try again.")

    days = parsed["days"]
    if len(days) != 7:
        raise ValueError("The AI did not return exactly 7 days. Please try again.")

    for index, day in enumerate(days, start=1):
        if day.get("day") != index:
            day["day"] = index
        meals = day.get("meals", [])
        if not isinstance(meals, list) or len(meals) < 3:
            raise ValueError(
                f"Day {index} is missing required meals. Please regenerate the plan."
            )

    return parsed


def validate_inputs(age: int, weight: float, height: float, budget: float) -> str | None:
    if not (18 <= age <= 100):
        return "Please enter an age between 18 and 100."
    if weight <= 0:
        return "Weight must be greater than 0."
    if height <= 0:
        return "Height must be greater than 0."
    if budget <= 0:
        return "Budget must be greater than 0."
    return None


def render_meal(meal: dict[str, Any]) -> None:
    name = meal.get("name", "Meal")
    desc = meal.get("description", "")
    considerations = normalize_list(meal.get("dietary_considerations"))
    search = meal.get("recipe_search") or name
    recipe_url = youtube_search_url(str(search))
    tags = "".join(f"<span class='tag'>{c}</span>" for c in considerations[:4])
    st.markdown(
        f"""
        <div class='meal-card'>
          <div class='meal-type'>{meal.get('type','Meal')}</div>
          <div class='meal-name'>{name}</div>
          <div class='meal-desc'>{desc}</div>
          <div style='margin-top:.45rem'>{tags}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.link_button("▶ Find recipe on YouTube", recipe_url)


# ---------- App state ----------
if "plan" not in st.session_state:
    st.session_state.plan = None
if "generated" not in st.session_state:
    st.session_state.generated = False

# ---------- Hero ----------
st.markdown(
    f"""
    <div class='hero'>
      <div class='eyebrow'>AI Nutrition & Wellness · Pakistan</div>
      <h1>{APP_NAME}</h1>
      <p>{TAGLINE} Build a practical 7-day plan around your goal, food preferences, allergies, health considerations, and PKR budget.</p>
      <div class='pill'>🥗 7-day planning · 🇵🇰 Pakistan-friendly · 🔒 allergy-aware</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

if st.session_state.plan is None:
    st.markdown("<div class='section-title'>Tell us about your needs</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>A few details help the planner make the week practical and relevant.</div>", unsafe_allow_html=True)

    with st.form("profile_form", clear_on_submit=False):
        st.markdown("### 1 · Personal profile")
        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.number_input("Age", min_value=18, max_value=100, value=22, step=1)
            gender = st.selectbox("Gender", ["Male", "Female"])
        with c2:
            unit_system = st.radio("Unit system", ["Metric", "Imperial"], horizontal=True)
            if unit_system == "Metric":
                weight = st.number_input("Weight (kg)", min_value=1.0, value=65.0, step=0.5)
                height = st.number_input("Height (cm)", min_value=1.0, value=165.0, step=0.5)
            else:
                weight = st.number_input("Weight (lb)", min_value=1.0, value=143.0, step=0.5)
                height = st.number_input("Height (in)", min_value=1.0, value=65.0, step=0.5)
        with c3:
            goal = st.selectbox("Primary goal", ["Lose Weight", "Maintain Weight", "Gain/Bulk"])
            st.caption("Your selected goal will shape the meal recommendations.")

        st.markdown("### 2 · Dietary preferences")
        c1, c2 = st.columns(2)
        with c1:
            restrictions = st.multiselect(
                "Dietary restrictions",
                ["Vegetarian", "Vegan", "Gluten-free", "Dairy-free", "Other"],
            )
            allergies = st.multiselect(
                "Food allergies · strict exclusions",
                ["Peanuts", "Nuts", "Eggs", "Milk", "Seafood", "Other"],
            )
            if "Other" in restrictions:
                restrictions_other = st.text_input("Other dietary restriction")
            else:
                restrictions_other = ""
            if "Other" in allergies:
                allergies_other = st.text_input("Other allergy")
            else:
                allergies_other = ""
        with c2:
            cuisines = st.multiselect(
                "Preferred cuisines",
                ["Pakistani", "Indian", "Italian", "Chinese", "Middle Eastern", "Other"],
                default=["Pakistani"],
            )
            health_conditions = st.multiselect(
                "Health considerations (optional)",
                ["Diabetes", "Hypertension", "High cholesterol", "PCOS", "Other"],
            )
            if "Other" in health_conditions:
                health_other = st.text_input("Other health consideration")
            else:
                health_other = ""

        st.markdown("### 3 · Budget")
        b1, b2 = st.columns([2, 1])
        with b1:
            budget = st.number_input("Budget (PKR)", min_value=1.0, value=5000.0, step=250.0)
        with b2:
            budget_frequency = st.selectbox("Budget frequency", ["per week", "per day"])
        st.markdown(
            "<div class='small-note'>Budget recommendations are estimates and not live market prices.</div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='warning'>⚕️ <b>Health & safety:</b> {DISCLAIMER}</div>", unsafe_allow_html=True)

        submitted = st.form_submit_button("✨ Generate my 7-day plan", type="primary", use_container_width=True)

    if submitted:
        error = validate_inputs(age, weight, height, budget)
        if error:
            st.error(error)
            st.stop()
        restrictions = [r for r in restrictions if r != "Other"] + ([restrictions_other] if restrictions_other else [])
        allergies = [a for a in allergies if a != "Other"] + ([allergies_other] if allergies_other else [])
        cuisines = [c for c in cuisines if c != "Other"]
        if not cuisines:
            cuisines = ["Pakistani"]
        health_conditions = [h for h in health_conditions if h != "Other"] + ([health_other] if health_other else [])
        profile = {
            "age": age,
            "gender": gender,
            "weight": weight,
            "height": height,
            "weight_unit": "kg" if unit_system == "Metric" else "lb",
            "height_unit": "cm" if unit_system == "Metric" else "in",
            "goal": goal,
            "restrictions": restrictions,
            "allergies": allergies,
            "cuisines": cuisines,
            "health_conditions": health_conditions,
            "budget_amount": budget,
            "budget_frequency": budget_frequency,
        }
        with st.spinner("Designing your week around your preferences…"):
            try:
                st.session_state.plan = generate_plan(profile)
                st.session_state.generated = True
                st.rerun()
            except Exception as exc:
                st.error(f"We couldn’t generate your meal plan right now. {exc}")
else:
    plan = st.session_state.plan
    st.markdown("<div class='section-title'>Your personalized week</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-sub'>{plan.get('summary','Your plan has been personalized to your selected preferences.')}</div>", unsafe_allow_html=True)

    stats = st.columns(4)
    for col, value, label in zip(stats, ["7", "3", "Strict", "PKR"], ["Days", "Core meals/day", "Allergy handling", "Budget-aware"]):
        with col:
            st.markdown(f"<div class='stat'><div class='big'>{value}</div><div class='small'>{label}</div></div>", unsafe_allow_html=True)

    for day in plan.get("days", []):
        day_num = day.get("day", "")
        fit = day.get("budget_fit", "")
        with st.expander(f"Day {day_num}  ·  {fit.title() if fit else 'Personalized plan'}", expanded=(day_num == 1)):
            meals = day.get("meals", [])
            for meal in meals:
                render_meal(meal)

    st.markdown(f"<div class='warning'>⚕️ <b>Important:</b> {DISCLAIMER}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
    if st.button("↺ Create a different plan", use_container_width=True):
        st.session_state.plan = None
        st.session_state.generated = False
        st.rerun()

st.markdown(f"<div class='footer'>© {APP_NAME} · General wellness and meal-planning support · Built for the hackathon MVP</div>", unsafe_allow_html=True)