
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

import pycountry
from babel.numbers import get_currency_name, get_currency_symbol, get_territory_currencies, list_currencies


CONTINENT_LABELS = {
    "AF": "🌍 Africa",
    "AN": "🧊 Antarctica",
    "AS": "🌏 Asia",
    "EU": "🌍 Europe",
    "NA": "🌎 North America",
    "SA": "🌎 South America",
    "OC": "🌺 Oceania",
}

# ISO alpha-2 -> broad continent. Based on the continent fields used by the
# open "Countries, Languages & Continents" dataset; a few territories are
# placed in the broad geographic region most useful for meal planning.
CONTINENT_CODES = {
    "AF": """DZ AO BJ BW BF BI CV CM CF TD KM CG CD CI DJ EG GQ ER SZ ET GA GM GH GN GW KE LS LR LY MG MW ML MR MU MA MZ NA NE NG RE RW SH SC SL SO ZA SS SD TZ TG TN UG EH ZM ZW AC YT SN ST""".split(),
    "AN": """AQ BV TF HM""".split(),
    "AS": """AF AM AZ BH BD BT BN IO KH CN CC CX GE HK IN ID IR IQ IL JP JO KZ KW KG LA LB MO MY MV MN MM NP KP OM PK PS PH QA SA SG KR LK SY TW TJ TH TL TR TM AE UZ VN YE""".split(),
    "EU": """AX AL AD AT BY BE BA BG HR CZ DK EE FO FI FR DE GI GR GG HU IS IE IM IT JE XK LV LI LT LU MT MD MC ME NL MK NO PL PT RO RU SM RS SK SI ES SJ SE CH UA GB VA CY""".split(),
    "NA": """AI AG AW BS BB BZ BM BQ CA KY CR CU CW DM DO SV GL GD GP GT HT HN JM MQ MX MS NI PA PR BL KN LC MF PM VC SX TT TC US VG VI""".split(),
    "SA": """AR BO BR CL CO EC FK GF GY PY PE GS SR UY VE""".split(),
    "OC": """AS AU CK FJ PF GU KI MH FM NR NC NZ NU NF MP PW PG PN WS SB TK TO TV UM VU WF""".split(),
}

CONTINENT_BY_CODE = {
    code: continent
    for continent, codes in CONTINENT_CODES.items()
    for code in codes
}

COMMON_NAME_OVERRIDES = {
    "Congo, The Democratic Republic of the": "Democratic Republic of the Congo",
    "Congo": "Republic of the Congo",
    "Côte d’Ivoire": "Côte d'Ivoire",
    "Korea, Republic of": "South Korea",
    "Korea, Democratic People's Republic of": "North Korea",
    "Lao People's Democratic Republic": "Laos",
    "Moldova, Republic of": "Moldova",
    "Palestine, State of": "Palestine",
    "Russian Federation": "Russia",
    "Syrian Arab Republic": "Syria",
    "Tanzania, United Republic of": "Tanzania",
    "Türkiye": "Turkey",
    "Venezuela, Bolivarian Republic of": "Venezuela",
    "Bolivia, Plurinational State of": "Bolivia",
    "Brunei Darussalam": "Brunei",
    "Iran, Islamic Republic of": "Iran",
    "Micronesia, Federated States of": "Micronesia",
    "Taiwan, Province of China": "Taiwan",
    "Viet Nam": "Vietnam",
    "Holy See (Vatican City State)": "Vatican City",
}

# Additional broad name used by many users, even though Kosovo does not have
# an official ISO 3166-1 assignment in pycountry.
EXTRA_REGIONS = [
    {"code": "XK", "name": "Kosovo", "continent": "EU", "currency": ["EUR"]},
    {"code": "WORLD", "name": "Global / mixed", "continent": "WORLD", "currency": []},
]


@dataclass(frozen=True)
class CountryRow:
    code: str
    name: str
    continent: str
    currency_codes: tuple[str, ...]


def _currency_codes(alpha2: str) -> tuple[str, ...]:
    try:
        values = get_territory_currencies(alpha2, tender=True, non_tender=False)
    except Exception:
        values = []
    return tuple(values)


def build_country_rows() -> list[CountryRow]:
    rows: list[CountryRow] = []
    for item in pycountry.countries:
        code = getattr(item, "alpha_2", "")
        if not code:
            continue
        continent = CONTINENT_BY_CODE.get(code, "AN")
        name = COMMON_NAME_OVERRIDES.get(item.name, item.name)
        rows.append(
            CountryRow(
                code=code,
                name=name,
                continent=continent,
                currency_codes=_currency_codes(code),
            )
        )
    rows.append(CountryRow("XK", "Kosovo", "EU", ("EUR",)))
    return sorted(rows, key=lambda x: (x.continent, x.name.lower()))


COUNTRY_ROWS = build_country_rows()

CONTINENT_ORDER = ["AF", "AS", "EU", "NA", "SA", "OC", "AN"]
COUNTRIES_BY_CONTINENT: dict[str, list[CountryRow]] = defaultdict(list)
for row in COUNTRY_ROWS:
    COUNTRIES_BY_CONTINENT[row.continent].append(row)


def currency_label(code: str) -> str:
    try:
        name = get_currency_name(code, locale="en")
    except Exception:
        name = code
    try:
        symbol = get_currency_symbol(code, locale="en")
    except Exception:
        symbol = code
    if not symbol or symbol == code:
        return f"{code} · {name}"
    return f"{code} · {symbol} · {name}"


# Collect current/tender currencies associated with countries and then append
# all current currency codes exposed by Babel's CLDR data.
_current_currency_codes: set[str] = set()
for row in COUNTRY_ROWS:
    _current_currency_codes.update(row.currency_codes)

# A few planning currencies may exist in CLDR even when no country in the
# selected set is using them as a tender currency.
for code in list_currencies():
    if code in _current_currency_codes:
        continue

CURRENCY_OPTIONS = [
    currency_label(code)
    for code in sorted(_current_currency_codes)
]

CURRENCY_CODE_BY_LABEL = {
    currency_label(code): code
    for code in sorted(_current_currency_codes)
}

COUNTRY_LABEL_BY_CODE = {row.code: row.name for row in COUNTRY_ROWS}
COUNTRY_ROW_BY_CODE = {row.code: row for row in COUNTRY_ROWS}


DIETARY_REQUIREMENTS = [
    "Vegetarian",
    "Vegan",
    "Lacto-vegetarian",
    "Ovo-vegetarian",
    "Lacto-ovo vegetarian",
    "Pescatarian",
    "Flexitarian",
    "Whole-food plant-based",
    "Plant-forward",
    "High-protein",
    "Low-carb",
    "Keto / very low-carb",
    "Low-fat",
    "Low-sodium",
    "Mediterranean-style",
    "DASH-style",
    "Gluten-free",
    "Dairy-free",
    "Egg-free",
    "Lactose-free",
    "Soy-free",
    "Nut-free",
    "Peanut-free",
    "Low-FODMAP",
    "Soft-food / easy-to-chew",
    "Texture-modified",
    "Halal",
    "Kosher",
    "Jain",
    "Hindu vegetarian",
    "Buddhist vegetarian",
    "Sattvic / yogic",
    "Sikh vegetarian preference",
    "Rastafari / Ital preference",
    "No added sugar",
    "Added-sugar conscious",
    "Whole-grain emphasis",
    "Heart-healthy style",
    "Other",
]

ALLERGIES = [
    "Peanuts",
    "Tree nuts",
    "Almonds",
    "Cashews",
    "Walnuts",
    "Pistachios",
    "Hazelnuts",
    "Eggs",
    "Milk / dairy",
    "Lactose",
    "Fish",
    "Shellfish",
    "Crustaceans",
    "Mollusks",
    "Sesame",
    "Soy",
    "Wheat",
    "Gluten",
    "Mustard",
    "Celery",
    "Lupin",
    "Sulphites / sulfites",
    "Corn / maize",
    "Legumes",
    "Chickpeas",
    "Lentils",
    "Coconut",
    "Kiwi",
    "Other",
]

HEALTH_CONSIDERATIONS = [
    "None / no specific consideration",
    "Diabetes",
    "Prediabetes",
    "High blood pressure",
    "High cholesterol",
    "High triglycerides",
    "PCOS",
    "Kidney-related condition",
    "Kidney stone history",
    "Gout",
    "Fatty liver",
    "IBS",
    "GERD / acid reflux",
    "Celiac disease",
    "Iron-deficiency anemia",
    "Vitamin D deficiency",
    "Pregnancy",
    "Breastfeeding",
    "Osteoporosis / bone health",
    "Heart-health considerations",
    "Digestive sensitivity",
    "Other",
]

FAITH_FOOD_PRACTICES = [
    "No specific faith-based food restriction",
    "Muslim / Halal",
    "Jewish / Kosher",
    "Jain food practice",
    "Hindu vegetarian preference",
    "Buddhist vegetarian preference",
    "Sikh vegetarian preference",
    "Rastafari / Ital preference",
    "Seventh-day Adventist vegetarian preference",
    "Other food-practice preference",
]

GOALS = [
    "Lose weight",
    "Maintain weight",
    "Gain weight",
    "Build muscle",
    "Improve strength / performance",
    "Improve endurance",
    "Body recomposition",
    "Eat healthier / balanced",
]

ACTIVITY_LEVELS = [
    "Mostly inactive",
    "Lightly active",
    "Moderately active",
    "Very active",
    "Athlete / highly active",
]

TRAINING_TYPES = [
    "No structured training",
    "Strength training",
    "Hypertrophy / muscle-building",
    "CrossFit / functional training",
    "Running",
    "Cycling",
    "Swimming",
    "Team sport",
    "Combat sport",
    "Dance / classes",
    "Mixed training",
]

WORKOUT_TIMES = [
    "Mostly mornings",
    "Mostly afternoons",
    "Mostly evenings",
    "Mixed / varies",
]

FITNESS_FOCUSES = [
    "General wellness",
    "Fat-loss support",
    "Muscle-building support",
    "Strength support",
    "Endurance support",
    "Recovery-friendly meals",
    "Pre-workout fueling",
    "Post-workout recovery meals",
    "Competition / event preparation",
]

BUDGET_FREQUENCIES = [
    "per meal",
    "per day",
    "per week",
    "per 2 weeks",
    "per month",
    "per 3 months",
    "per 6 months",
    "per 9 months",
    "per year",
]

VARIETY_OPTIONS = [
    "Balanced variety",
    "High variety",
    "Simple & repetitive",
    "Meal-prep friendly",
    "Leftover-friendly",
    "Family-friendly",
    "Quick weekday meals",
    "Seasonal variety",
    "Budget-first simplicity",
    "Adventurous flavors",
    "Minimal ingredients",
    "Batch-cooking focus",
]

COOKING_TIME_OPTIONS = [
    "10 minutes or less",
    "15–20 minutes",
    "30 minutes or less",
    "45 minutes or less",
    "I enjoy longer cooking",
]

KITCHEN_OPTIONS = [
    "Full kitchen",
    "Basic kitchen",
    "Limited cooking equipment",
    "Mostly no-cook / ready-to-eat",
]

COMMON_FOODS = [
    "Chicken", "Beef", "Mutton / lamb", "Fish", "Eggs", "Dairy / yogurt",
    "Rice", "Roti / flatbread", "Oats", "Potatoes", "Pasta", "Beans",
    "Lentils / daal", "Chickpeas / chana", "Tofu", "Tempeh",
    "Leafy greens", "Tomatoes", "Cucumber", "Carrots", "Bananas",
    "Apples", "Berries", "Mango", "Dates", "Nuts", "Seeds",
]

# Broad country/region cuisine labels. The second cuisine selector in the app
# also exposes every supported country as a "country-inspired food style".
CUISINE_REGIONS = [
    "South Asia · Pakistani",
    "South Asia · Indian",
    "South Asia · Bangladeshi",
    "South Asia · Sri Lankan",
    "South Asia · Nepalese",
    "South Asia · Bhutanese",
    "Southeast Asia · Indonesian",
    "Southeast Asia · Malaysian",
    "Southeast Asia · Singaporean",
    "Southeast Asia · Thai",
    "Southeast Asia · Vietnamese",
    "Southeast Asia · Filipino",
    "East Asia · Chinese",
    "East Asia · Japanese",
    "East Asia · Korean",
    "East Asia · Taiwanese",
    "Central Asia · Uzbek",
    "Central Asia · Kazakh",
    "Central Asia · Kyrgyz",
    "Central Asia · Tajik",
    "Central Asia · Turkmen",
    "Middle East · Arabian Gulf",
    "Middle East · Levantine",
    "Middle East · Iranian / Persian",
    "Middle East · Iraqi",
    "Middle East · Turkish",
    "Caucasus · Georgian",
    "Caucasus · Armenian",
    "Caucasus · Azerbaijani",
    "North Africa · Moroccan",
    "North Africa · Algerian",
    "North Africa · Tunisian",
    "North Africa · Egyptian",
    "East Africa · Ethiopian",
    "East Africa · Eritrean",
    "East Africa · Somali",
    "East Africa · Kenyan",
    "Southern Africa · South African",
    "West Africa · Nigerian",
    "West Africa · Ghanaian",
    "West Africa · Senegalese",
    "Central Africa · Congolese",
    "Mediterranean · Greek",
    "Mediterranean · Italian",
    "Mediterranean · Spanish",
    "Mediterranean · Southern French",
    "Europe · British",
    "Europe · Irish",
    "Europe · German",
    "Europe · Austrian",
    "Europe · Swiss",
    "Europe · Polish",
    "Europe · Czech",
    "Europe · Hungarian",
    "Europe · Balkan",
    "Europe · Nordic",
    "Europe · Baltic",
    "Europe · Portuguese",
    "Europe · Romanian",
    "Europe · Ukrainian",
    "North America · American",
    "North America · Canadian",
    "North America · Mexican",
    "Central America · Guatemalan",
    "Central America · Salvadoran",
    "Central America · Costa Rican",
    "Caribbean · Cuban",
    "Caribbean · Jamaican",
    "Caribbean · Dominican",
    "Caribbean · Trinidadian",
    "South America · Brazilian",
    "South America · Argentine",
    "South America · Peruvian",
    "South America · Chilean",
    "South America · Colombian",
    "South America · Venezuelan",
    "South America · Bolivian",
    "Oceania · Australian",
    "Oceania · New Zealand",
    "Oceania · Polynesian",
    "Oceania · Melanesian",
    "Oceania · Micronesian",
    "Global · Mediterranean",
    "Global · Latin American",
    "Global · Asian-inspired",
    "Global · Comfort food",
    "Global · High-protein",
    "Global · Plant-forward",
    "Other",
]

COUNTRY_INSPIRED_CUISINES = [
    f"{row.name} · country-inspired"
    for row in COUNTRY_ROWS
    if row.code != "AQ"
]
