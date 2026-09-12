NourishAI Pakistan — PRD Reference & Current Product Notes

1. Source PRD

Source: AI-Powered Personalized Diet Planner PRD v1.0

Original target market: Pakistan

Original platform: Streamlit web application

The source PRD defines the initial MVP as a personalized 7-day meal-planning experience that collects profile information, goals, dietary constraints, allergies, health considerations, preferred cuisines, and PKR budget, then generates a practical meal plan with recipe resources.

2. Original MVP

Inputs

Personal profile

Goal

Dietary requirements

Allergies

Health considerations

Preferred cuisines

PKR budget

Output

Personalized 7-day meal plan

Breakfast

Lunch

Dinner

Optional snacks

Recipe resources

Budget-aware recommendations

Culturally relevant food suggestions

Original product principles

Keep the experience simple and practical.

Treat allergies as strict exclusions.

Use Halal as a default dietary constraint in the original Pakistan-focused MVP.

Consider health conditions as dietary considerations rather than diagnoses.

Avoid fabricated recipe URLs.

Prefer practical and commonly available foods.

Prioritize a reliable end-to-end MVP over unnecessary complexity.

3. Original Out-of-Scope Items

The source PRD explicitly lists the following as out of scope for the original MVP:

Calorie or macro calculations

Real-time food prices

Grocery delivery

User accounts/login

Progress tracking

Wearable integration

Medical diagnosis

Medication recommendations

Personalized medical treatment

Guaranteed medical outcomes

Halal certification / verification

4. Current Product Extensions

The current application has evolved beyond the original PRD in several areas.

These are implementation extensions, not changes to what the source PRD originally required.

Accounts and identity

Register

Sign in

Sign out

Forgot password

Set/change password

Per-user saved-plan history

Plan management

Save generated plans

View plan history

Delete saved plans

Reopen saved plans

Export plans to professional Word documents

Broader planning context

The current implementation additionally supports:

Multiple planning periods

Fitness / gym goals

Activity level

Training type

Workout timing

Food likes/dislikes

Broader dietary requirements

Broader allergy selections

Broader health considerations

Religion / food-practice preferences

Global country/region context

Cuisine-region and country-inspired cuisine selections

Multiple currencies

Expanded budget cadences

Meal variety preferences

5. Current Product Direction

The product direction is now:

A universal AI nutrition planning studio with a Pakistan-first origin.

The application should still provide strong support for Pakistani food culture, but the architecture is designed to work across countries, currencies, cuisines, dietary systems, and food practices.

6. AI Safety Requirements

The AI layer must:

Respect declared dietary restrictions.

Treat declared allergies as strict exclusions.

Consider the user's stated goal.

Consider food preferences and cuisine context.

Consider budget constraints as estimates rather than live market prices.

Consider health conditions cautiously as user-provided dietary context.

Avoid diagnosis and treatment claims.

Avoid medication recommendations.

Avoid guaranteed outcomes.

Avoid unsupported religious or certification claims.

Avoid fabricated recipe URLs.

7. Success Criteria

The current product should reliably support this end-to-end path:

User context
    ↓
Validation
    ↓
Constraint understanding
    ↓
AI personalization
    ↓
Meal-plan generation
    ↓
Structured display
    ↓
Save to user history
    ↓
Download / revisit

The original PRD's central success condition remains important: the user should provide their information and receive a practical personalized meal plan through a reliable Streamlit experience.

8. Hackathon Scope Guidance

The hackathon version should prioritize:

Reliable generation

Strong constraint handling

Clean, professional UI

Working deployment

Public GitHub repository

Clear PRD

Demonstrable user journey

Stable save/download functionality

Avoid adding complex features that make the core generation flow unreliable.

9. Safety Disclaimer

NourishAI provides general informational and meal-planning support. It does not diagnose diseases, prescribe medication, provide personalized medical treatment, or guarantee health outcomes. Users with medical conditions should consult a qualified healthcare professional before making significant dietary changes.

10. Documentation Status

This document separates the source PRD requirements from the current implementation extensions so the team can clearly explain what was part of the original hackathon MVP and what was added later.