from __future__ import annotations

import html
import json
import os
import re
import smtplib
import sqlite3
import secrets
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from io import BytesIO
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Inches, Pt, RGBColor

from storage import (
    authenticate_user,
    create_reset_request,
    create_user,
    delete_saved_plan,
    get_reset_request,
    get_saved_plan,
    initialize_database,
    list_saved_plans,
    mark_reset_used,
    update_password,
    validate_password_strength,
    save_plan_for_user,
)

from catalog import (
    ACTIVITY_LEVELS,
    ALLERGIES,
    BUDGET_FREQUENCIES,
    COMMON_FOODS,
    CONTINENT_LABELS,
    CONTINENT_ORDER,
    COUNTRIES_BY_CONTINENT,
    COUNTRY_INSPIRED_CUISINES,
    COUNTRY_ROW_BY_CODE,
    CURRENCY_CODE_BY_LABEL,
    CURRENCY_OPTIONS,
    COOKING_TIME_OPTIONS,
    CUISINE_REGIONS,
    DIETARY_REQUIREMENTS,
    FAITH_FOOD_PRACTICES,
    FITNESS_FOCUSES,
    GOALS,
    HEALTH_CONSIDERATIONS,
    KITCHEN_OPTIONS,
    TRAINING_TYPES,
    WORKOUT_TIMES,
    VARIETY_OPTIONS,
)

load_dotenv()

APP_NAME = "NourishAI"
VERSION = "4.1 Universal · Adaptive Plan Scopes"
TAGLINE = "Personalized food planning that adapts to your world, your routine, and your goals."
PLAN_SCOPES = [
    "Per meal · 1 meal",
    "Per day · 1 day",
    "Per week · 7 days",
    "Per month · 28 days (4 weeks)",
]
DISCLAIMER = (
    "NourishAI provides general wellness and meal-planning guidance. It does not diagnose "
    "conditions, prescribe treatment or medication, or replace a qualified doctor or dietitian. "
    "People with medical conditions, pregnancy, kidney-related conditions, eating disorders, "
    "or other complex needs should seek individualized professional advice."
)

st.set_page_config(
    page_title=f"{APP_NAME} · Universal Nutrition Studio",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Premium visual system
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@700;800&display=swap');

    :root {
      --bg: #f4f8f6;
      --surface: rgba(255,255,255,.86);
      --white: #ffffff;
      --ink: #0d2d29;
      --muted: #61756f;
      --line: rgba(16, 61, 54, .11);
      --teal: #0e8f7d;
      --teal-2: #06766a;
      --deep: #072f2b;
      --lime: #d8f46c;
      --mint: #dff7ef;
      --cyan: #8cf0dd;
      --lavender: #ddd5ff;
      --peach: #ffd9c4;
      --rose: #ffb6cf;
      --amber: #ffd98a;
      --shadow: 0 18px 65px rgba(15,55,49,.08);
    }

    html, body, [class*="css"] {
      font-family: 'DM Sans', sans-serif;
    }

    .stApp {
      background:
        radial-gradient(circle at 5% 2%, rgba(216,244,108,.18), transparent 22%),
        radial-gradient(circle at 95% 6%, rgba(221,213,255,.28), transparent 24%),
        radial-gradient(circle at 85% 82%, rgba(255,182,207,.10), transparent 23%),
        linear-gradient(180deg, #f8fbfa 0%, #f3f8f6 100%);
      color: var(--ink);
    }

    .block-container {
      max-width: 1260px;
      padding: 1rem 1.5rem 4.25rem;
    }

    #MainMenu { visibility: hidden; }
    header { background: transparent !important; }
    footer { visibility: hidden; }

    .topbar {
      display:flex;
      justify-content:space-between;
      align-items:center;
      gap:1rem;
      margin: .15rem 0 1rem;
      animation: enter .55s ease both;
    }

    .brand {
      display:flex;
      align-items:center;
      gap:.8rem;
    }

    .brand-mark {
      position:relative;
      width:48px;
      height:48px;
      display:grid;
      place-items:center;
      border-radius:16px;
      color:#fff;
      font-size:1.45rem;
      background:
        radial-gradient(circle at 25% 20%, rgba(255,255,255,.5), transparent 25%),
        linear-gradient(135deg, var(--teal), #32c2a8 55%, #8ae48a);
      box-shadow:0 14px 30px rgba(14,143,125,.22);
      animation: markFloat 5.5s ease-in-out infinite;
    }

    .brand-name {
      font-family:'Manrope',sans-serif;
      font-size:1.08rem;
      font-weight:800;
      letter-spacing:-.035em;
    }

    .brand-meta {
      color:var(--muted);
      font-size:.73rem;
      margin-top:.08rem;
    }

    .version-badge {
      padding:.43rem .7rem;
      border-radius:999px;
      background:rgba(255,255,255,.72);
      border:1px solid var(--line);
      color:var(--muted);
      font-size:.72rem;
      box-shadow:0 10px 30px rgba(25,60,54,.05);
      backdrop-filter:blur(10px);
    }

    .hero {
      position:relative;
      overflow:hidden;
      min-height:360px;
      border-radius:36px;
      padding:3.2rem 3.25rem;
      color:#fff;
      background:
        radial-gradient(circle at 83% 26%, rgba(216,244,108,.28), transparent 18%),
        radial-gradient(circle at 70% 95%, rgba(140,240,221,.18), transparent 24%),
        linear-gradient(125deg, #083e38 0%, #0a7568 44%, #0b9d88 100%);
      box-shadow:0 32px 100px rgba(7,65,58,.22);
      animation:heroIn .8s cubic-bezier(.2,.82,.2,1) both;
    }

    .hero::before {
      content:"";
      position:absolute;
      width:340px;
      height:340px;
      right:-95px;
      top:-135px;
      border-radius:50%;
      border:1px solid rgba(255,255,255,.12);
      box-shadow:
        0 0 0 30px rgba(255,255,255,.025),
        0 0 0 60px rgba(255,255,255,.018),
        0 0 0 90px rgba(255,255,255,.012);
      animation:breathe 7s ease-in-out infinite;
    }

    .hero::after {
      content:"";
      position:absolute;
      width:140px;
      height:140px;
      right:16%;
      bottom:-70px;
      border-radius:50%;
      background:rgba(216,244,108,.12);
      filter:blur(12px);
      animation:float 6.5s ease-in-out infinite;
    }

    .hero-grid {
      position:relative;
      z-index:2;
      display:grid;
      grid-template-columns:minmax(0,1fr) 280px;
      gap:1.75rem;
      align-items:end;
    }

    .eyebrow {
      text-transform:uppercase;
      letter-spacing:.17em;
      font-size:.69rem;
      font-weight:800;
      color:#caf8ed;
    }

    .hero h1 {
      font-family:'Manrope',sans-serif;
      font-size:clamp(3rem, 8vw, 6.2rem);
      line-height:.9;
      letter-spacing:-.065em;
      margin:.55rem 0 1rem;
    }

    .hero-copy {
      max-width:780px;
      color:rgba(255,255,255,.84);
      font-size:1.03rem;
      line-height:1.72;
    }

    .hero-pills {
      display:flex;
      flex-wrap:wrap;
      gap:.52rem;
      margin-top:1.25rem;
    }

    .hero-pill {
      padding:.48rem .72rem;
      border-radius:999px;
      border:1px solid rgba(255,255,255,.14);
      background:rgba(255,255,255,.08);
      color:#f2fffc;
      font-size:.76rem;
      backdrop-filter:blur(12px);
      transition:transform .2s ease, background .2s ease;
    }

    .hero-pill:hover {
      transform:translateY(-2px);
      background:rgba(255,255,255,.14);
    }

    .orb {
      position:relative;
      width:230px;
      height:230px;
      margin-left:auto;
      border-radius:50%;
      background:
        radial-gradient(circle at 34% 25%, rgba(255,255,255,.98), rgba(216,244,108,.9) 18%, rgba(66,206,177,.66) 43%, rgba(13,68,61,.18) 70%, transparent 71%);
      filter:drop-shadow(0 24px 44px rgba(0,0,0,.2));
      animation:float 6s ease-in-out infinite;
    }

    .orb::before,
    .orb::after {
      content:"";
      position:absolute;
      inset:23px;
      border-radius:50%;
      border:1px solid rgba(255,255,255,.26);
    }

    .orb::after {
      inset:52px;
      border-color:rgba(255,255,255,.17);
    }

    .orb span {
      position:absolute;
      inset:10px;
      border-radius:50%;
      border-top:1px solid rgba(255,255,255,.5);
      border-right:1px solid rgba(255,255,255,.12);
      animation:spin 19s linear infinite;
    }

    .section-head {
      margin:2rem 0 1rem;
      animation:enter .6s ease both;
    }

    .section-kicker {
      color:var(--teal);
      text-transform:uppercase;
      letter-spacing:.14em;
      font-size:.68rem;
      font-weight:800;
    }

    .section-title {
      font-family:'Manrope',sans-serif;
      font-size:1.72rem;
      font-weight:800;
      letter-spacing:-.04em;
      margin:.15rem 0 .3rem;
    }

    .section-sub {
      color:var(--muted);
      font-size:.88rem;
      line-height:1.55;
    }

    .feature-strip {
      display:grid;
      grid-template-columns:repeat(4,1fr);
      gap:.7rem;
      margin:1.15rem 0 1.25rem;
    }

    .feature-card {
      min-height:92px;
      padding:1rem;
      border-radius:20px;
      border:1px solid var(--line);
      background:rgba(255,255,255,.70);
      box-shadow:var(--shadow);
      backdrop-filter:blur(18px);
      animation:enter .6s ease both;
      transition:transform .2s ease, box-shadow .2s ease;
    }

    .feature-card:hover {
      transform:translateY(-3px);
      box-shadow:0 22px 60px rgba(18,60,52,.11);
    }

    .feature-emoji { font-size:1.15rem; }
    .feature-title { font-weight:800; font-size:.84rem; margin-top:.35rem; }
    .feature-copy { color:var(--muted); font-size:.69rem; line-height:1.45; margin-top:.1rem; }

    .glass {
      padding:1.1rem 1.15rem;
      border-radius:26px;
      border:1px solid var(--line);
      background:rgba(255,255,255,.70);
      box-shadow:var(--shadow);
      backdrop-filter:blur(18px);
    }

    .tab-caption {
      margin-bottom:.65rem;
      color:var(--muted);
      font-size:.76rem;
    }

    .micro {
      color:var(--muted);
      font-size:.72rem;
      line-height:1.45;
    }

    .hint {
      color:var(--muted);
      font-size:.71rem;
      line-height:1.5;
      margin-top:.15rem;
    }

    .soft-note {
      padding:.72rem .85rem;
      border:1px solid rgba(14,143,125,.10);
      background:linear-gradient(135deg, rgba(223,247,239,.75), rgba(255,255,255,.68));
      border-radius:15px;
      color:#44615a;
      font-size:.74rem;
      line-height:1.5;
      margin:.45rem 0;
    }

    .safety {
      border-radius:18px;
      padding:.95rem 1rem;
      background:linear-gradient(135deg, rgba(255,246,221,.92), rgba(255,255,255,.78));
      border:1px solid rgba(221,174,74,.28);
      color:#70541d;
      font-size:.76rem;
      line-height:1.55;
      box-shadow:0 10px 28px rgba(114,84,29,.06);
    }

    .cta-panel {
      position:relative;
      overflow:visible;
      margin-top:1rem;
      padding:0;
      border:0;
      background:transparent;
    }

    .result-hero {
      position:relative;
      overflow:hidden;
      border-radius:28px;
      padding:1.45rem 1.55rem;
      color:#fff;
      background:
        radial-gradient(circle at 86% 15%, rgba(216,244,108,.26), transparent 18%),
        linear-gradient(130deg, #063e38 0%, #0b7669 48%, #0f9c87 100%);
      box-shadow:0 24px 80px rgba(8,72,63,.18);
      animation:heroIn .65s ease both;
    }

    .result-hero::after {
      content:"✦";
      position:absolute;
      right:10%;
      top:18%;
      font-size:5rem;
      color:rgba(255,255,255,.09);
      animation:float 6s ease-in-out infinite;
    }

    .result-eyebrow {
      text-transform:uppercase;
      letter-spacing:.14em;
      color:#c6f4e9;
      font-size:.67rem;
      font-weight:800;
    }

    .result-title {
      font-family:'Manrope',sans-serif;
      font-size:2.0rem;
      font-weight:800;
      letter-spacing:-.04em;
      margin:.18rem 0 .4rem;
    }

    .result-copy {
      max-width:920px;
      font-size:.87rem;
      line-height:1.62;
      color:rgba(255,255,255,.86);
    }

    .metric-grid {
      display:grid;
      grid-template-columns:repeat(5,1fr);
      gap:.7rem;
      margin:1rem 0;
    }

    .metric-card {
      border:1px solid var(--line);
      border-radius:18px;
      background:rgba(255,255,255,.72);
      padding:.88rem .95rem;
      box-shadow:0 12px 34px rgba(18,58,51,.06);
      transition:transform .2s ease;
      animation:enter .5s ease both;
    }

    .metric-card:hover { transform:translateY(-3px); }
    .metric-value { font-family:'Manrope',sans-serif; font-size:1.18rem; font-weight:800; letter-spacing:-.03em; }
    .metric-label { color:var(--muted); font-size:.68rem; margin-top:.17rem; }

    .day-card {
      border-radius:23px;
      padding:1rem;
      border:1px solid var(--line);
      background:rgba(255,255,255,.72);
      box-shadow:var(--shadow);
    }

    .day-heading {
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:.7rem;
    }

    .day-number {
      display:inline-flex;
      align-items:center;
      justify-content:center;
      width:38px;
      height:38px;
      border-radius:13px;
      background:linear-gradient(135deg, var(--teal), #39bea6);
      color:#fff;
      font-weight:800;
      box-shadow:0 10px 22px rgba(14,143,125,.19);
    }

    .day-title {
      font-family:'Manrope',sans-serif;
      font-size:1.06rem;
      font-weight:800;
      margin-left:.55rem;
    }

    .budget-chip {
      padding:.34rem .55rem;
      border-radius:999px;
      font-size:.66rem;
      font-weight:800;
      color:var(--teal-2);
      background:#edf9f5;
      border:1px solid #d8ede8;
    }

    .day-note {
      color:var(--muted);
      font-size:.76rem;
      line-height:1.45;
      margin:.55rem 0 .7rem;
    }

    .meal {
      position:relative;
      overflow:hidden;
      padding:1rem 1.05rem 1.05rem;
      margin:.65rem 0;
      border-radius:19px;
      border:1px solid var(--line);
      background:rgba(255,255,255,.78);
      box-shadow:0 12px 30px rgba(20,60,53,.045);
      transition:transform .22s ease, box-shadow .22s ease;
      animation:enter .48s ease both;
    }

    .meal:nth-of-type(2) { animation-delay:.04s; }
    .meal:nth-of-type(3) { animation-delay:.08s; }
    .meal:nth-of-type(4) { animation-delay:.12s; }
    .meal:hover {
      transform:translateY(-2px);
      box-shadow:0 18px 45px rgba(20,60,53,.09);
    }

    .meal::before {
      content:"";
      position:absolute;
      left:0;
      top:0;
      bottom:0;
      width:4px;
      background:linear-gradient(180deg, #0e8f7d, #d8f46c, #ffb6cf);
    }

    .meal-type {
      color:var(--teal);
      text-transform:uppercase;
      letter-spacing:.12em;
      font-size:.64rem;
      font-weight:800;
    }

    .meal-name {
      font-size:1.02rem;
      font-weight:800;
      margin:.16rem 0 .25rem;
    }

    .meal-desc {
      color:#506862;
      font-size:.80rem;
      line-height:1.55;
    }

    .tag {
      display:inline-block;
      margin:.5rem .22rem 0 0;
      padding:.27rem .49rem;
      border-radius:999px;
      color:#0b685c;
      background:#eff9f6;
      border:1px solid #dceee9;
      font-size:.65rem;
    }

    .recipe-box {
      margin-top:.62rem;
      padding:.64rem .7rem;
      border-radius:13px;
      border:1px solid rgba(117,99,184,.12);
      background:linear-gradient(135deg, rgba(237,233,255,.50), rgba(255,255,255,.68));
    }

    .footer {
      text-align:center;
      color:#71837f;
      font-size:.70rem;
      padding-top:2.5rem;
    }

    /* Native Streamlit controls */
    .stButton > button,
    .stFormSubmitButton > button,
    .stDownloadButton > button,
    .stLinkButton > a {
      border-radius:14px !important;
      min-height:45px !important;
      font-weight:800 !important;
      border:1px solid var(--line) !important;
      transition:transform .18s ease, box-shadow .18s ease, filter .18s ease !important;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover,
    .stDownloadButton > button:hover,
    .stLinkButton > a:hover {
      transform:translateY(-2px);
      box-shadow:0 14px 28px rgba(13,69,59,.13);
      filter:saturate(1.08);
    }

    .stFormSubmitButton > button[kind="primary"] {
      color:#fff !important;
      border:0 !important;
      background:
        radial-gradient(circle at 15% 25%, rgba(255,255,255,.18), transparent 24%),
        linear-gradient(115deg, #0c7d70, #10aa91, #6ad59c) !important;
      box-shadow:0 16px 34px rgba(14,143,125,.24) !important;
    }

    .stDownloadButton > button {
      background:linear-gradient(135deg,#f9f8ff,#fff) !important;
    }

    .stProgress > div > div {
      background:linear-gradient(90deg,#0e8f7d,#71d89e,#d8f46c) !important;
    }

    [data-testid="stTabs"] button {
      border-radius:999px !important;
      padding:.55rem .9rem !important;
      margin-right:.3rem;
      border:1px solid transparent !important;
      transition:all .2s ease !important;
    }

    [data-testid="stTabs"] button[aria-selected="true"] {
      background:linear-gradient(135deg,#e2f8f2,#f6fff9) !important;
      color:var(--teal-2) !important;
      border-color:rgba(14,143,125,.18) !important;
      box-shadow:0 8px 18px rgba(14,143,125,.08);
    }

    [data-testid="stSelectbox"] > div > div,
    [data-testid="stMultiSelect"] > div > div,
    [data-testid="stNumberInput"] > div > div,
    [data-testid="stTextInput"] > div > div,
    [data-testid="stTextArea"] > div > div {
      border-radius:14px !important;
    }

    [data-baseweb="tag"] {
      border-radius:999px !important;
      background:linear-gradient(135deg,#def7ef,#e9ffe0) !important;
      color:#0a6a5e !important;
      border:1px solid rgba(14,143,125,.10) !important;
    }

    .stAlert {
      border-radius:16px !important;
    }

    /* Authentication / account experience */
    .auth-page {
      min-height: calc(100vh - 3rem);
      display:grid;
      place-items:center;
      padding: 2rem 0 3.5rem;
    }
    .auth-wrap {
      width:min(1080px, 100%);
      display:grid;
      grid-template-columns:1.05fr .95fr;
      border:1px solid rgba(13,45,41,.09);
      border-radius:34px;
      overflow:hidden;
      background:rgba(255,255,255,.72);
      box-shadow:0 35px 110px rgba(7,65,58,.13);
      backdrop-filter:blur(18px);
      animation:heroIn .65s cubic-bezier(.2,.82,.2,1) both;
    }
    .auth-promo {
      position:relative;
      overflow:hidden;
      min-height:610px;
      padding:3rem;
      color:#fff;
      background:
        radial-gradient(circle at 82% 18%, rgba(216,244,108,.30), transparent 17%),
        radial-gradient(circle at 18% 85%, rgba(140,240,221,.18), transparent 23%),
        linear-gradient(145deg,#073b36 0%,#087768 46%,#10a58f 100%);
    }
    .auth-promo:before,
    .auth-promo:after {
      content:"";
      position:absolute;
      border-radius:999px;
      border:1px solid rgba(255,255,255,.12);
      animation:breathe 8s ease-in-out infinite;
    }
    .auth-promo:before { width:320px;height:320px;right:-100px;top:-70px; }
    .auth-promo:after { width:180px;height:180px;left:-85px;bottom:-55px;animation-delay:-2.5s; }
    .auth-promo .mini-logo { position:relative; z-index:2; display:flex; align-items:center; gap:.7rem; }
    .auth-promo .mini-logo-mark { width:44px;height:44px;display:grid;place-items:center;border-radius:14px;background:rgba(255,255,255,.13);font-size:1.25rem;box-shadow:inset 0 1px 0 rgba(255,255,255,.15); }
    .auth-promo h1 { position:relative;z-index:2;margin:3.3rem 0 0;font-family:'Manrope',sans-serif;font-size:clamp(2.8rem,5.5vw,5.8rem);line-height:.92;letter-spacing:-.065em; }
    .auth-promo p { position:relative;z-index:2;max-width:470px;margin:1.15rem 0 0;color:rgba(255,255,255,.82);line-height:1.7; }
    .auth-pills { position:absolute;z-index:2;left:3rem;right:3rem;bottom:2.2rem;display:flex;flex-wrap:wrap;gap:.55rem; }
    .auth-pill { padding:.5rem .7rem;border-radius:999px;border:1px solid rgba(255,255,255,.16);background:rgba(255,255,255,.08);font-size:.78rem; }
    .auth-form-pane { padding:2.25rem;display:flex;flex-direction:column;justify-content:center;background:rgba(255,255,255,.76); }
    .auth-eyebrow { color:var(--teal-2);font-size:.72rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase; }
    .auth-heading { margin:.4rem 0 .35rem;font-family:'Manrope',sans-serif;font-size:2rem;letter-spacing:-.045em; }
    .auth-copy { color:var(--muted);line-height:1.55;margin-bottom:1.3rem; }
    .auth-nav { display:flex;gap:.4rem;padding:.35rem;border:1px solid var(--line);background:#f7fbf9;border-radius:15px;margin-bottom:1.25rem; }
    .auth-nav-item { flex:1;padding:.6rem .45rem;text-align:center;border-radius:11px;color:var(--muted);font-size:.8rem;font-weight:700;cursor:pointer; }
    .auth-nav-item.active { color:var(--deep);background:#fff;box-shadow:0 5px 18px rgba(14,143,125,.09); }
    .auth-help { color:var(--muted);font-size:.76rem;line-height:1.5;margin-top:.45rem; }
    .auth-link-row { display:flex;justify-content:space-between;gap:.6rem;align-items:center;margin-top:.65rem; }
    .auth-link { color:var(--teal-2);font-size:.82rem;font-weight:700; }
    .password-rules { display:grid;grid-template-columns:1fr 1fr;gap:.35rem .65rem;padding:.75rem .8rem;margin:.55rem 0 1rem;border-radius:14px;background:#f5faf8;border:1px solid var(--line);font-size:.76rem;color:var(--muted); }
    .rule-ok { color:#0b806f;font-weight:700; }
    .rule-off { color:#7a8b86; }
    .flash-success { border-radius:14px;padding:.8rem .95rem;background:#e8fbf4;border:1px solid #bfeedd;color:#0a6f5f;font-size:.86rem;font-weight:600;margin-bottom:1rem; }
    .flash-error { border-radius:14px;padding:.8rem .95rem;background:#fff0f2;border:1px solid #f3c8d1;color:#a42644;font-size:.86rem;font-weight:600;margin-bottom:1rem; }
    .settings-card { max-width:850px;margin:0 auto;padding:1.4rem;border:1px solid var(--line);border-radius:24px;background:rgba(255,255,255,.76);box-shadow:var(--shadow); }

    @keyframes enter {
      from {opacity:0; transform:translateY(10px)}
      to {opacity:1; transform:translateY(0)}
    }

    @keyframes heroIn {
      from {opacity:0; transform:translateY(18px) scale(.988)}
      to {opacity:1; transform:translateY(0) scale(1)}
    }

    @keyframes float {
      0%,100% {transform:translateY(0)}
      50% {transform:translateY(-10px)}
    }

    @keyframes breathe {
      0%,100% {transform:scale(1); opacity:.82}
      50% {transform:scale(1.05); opacity:1}
    }

    @keyframes spin {
      to {transform:rotate(360deg)}
    }

    @keyframes markFloat {
      0%,100% {transform:translateY(0) rotate(0deg)}
      50% {transform:translateY(-3px) rotate(1.5deg)}
    }



    .auth-shell {
      max-width: 760px;
      margin: 7vh auto 1.4rem;
      padding: 2rem 2.1rem;
      border-radius:30px;
      color:#fff;
      background:
        radial-gradient(circle at 85% 18%, rgba(216,244,108,.28), transparent 20%),
        linear-gradient(130deg,#063e38,#0b7669 52%,#10a38c);
      box-shadow:0 28px 90px rgba(5,65,58,.18);
      animation:heroIn .7s ease both;
    }
    .auth-brand { display:flex; align-items:center; gap:.75rem; }
    .auth-brand span { display:grid; place-items:center; width:48px; height:48px; border-radius:15px; background:rgba(255,255,255,.13); font-size:1.3rem; }
    .auth-brand b { display:block; font-family:'Manrope',sans-serif; font-size:1.12rem; }
    .auth-brand small { color:rgba(255,255,255,.72); }
    .auth-title { margin-top:1.5rem; font-family:'Manrope',sans-serif; font-size:clamp(2.25rem,5vw,4.2rem); font-weight:800; letter-spacing:-.06em; line-height:.95; }
    .auth-subtitle { max-width:650px; margin-top:.85rem; color:rgba(255,255,255,.82); line-height:1.6; }
    .auth-card { max-width:760px; margin:0 auto; padding:1.2rem; border-radius:26px; background:rgba(255,255,255,.78); border:1px solid var(--line); box-shadow:var(--shadow); backdrop-filter:blur(18px); }
    @media (max-width: 900px) {
      .hero {padding:2rem 1.4rem; min-height:0;}
      .hero-grid {grid-template-columns:1fr;}
      .orb {width:140px;height:140px;margin:0 0 0 auto;}
      .feature-strip {grid-template-columns:repeat(2,1fr);}
      .metric-grid {grid-template-columns:repeat(2,1fr);}
    }

    @media (max-width: 620px) {
      .block-container {padding-left:.9rem;padding-right:.9rem;}
      .feature-strip {grid-template-columns:1fr;}
      .metric-grid {grid-template-columns:1fr 1fr;}
      .hero h1 {font-size:3rem;}
    }
    @media (max-width: 900px) {
      .auth-wrap {grid-template-columns:1fr;}
      .auth-promo {min-height:390px;padding:2.2rem;}
      .auth-promo h1 {margin-top:2.4rem;}
      .auth-pills {left:2.2rem;right:2.2rem;bottom:1.5rem;}
      .auth-form-pane {padding:1.4rem;}
    }
    @media (max-width: 560px) {
      .block-container {padding-left:.7rem;padding-right:.7rem;}
      .auth-page {padding-top:.4rem;}
      .auth-promo {min-height:340px;padding:1.5rem;}
      .auth-promo h1 {font-size:3rem;}
      .auth-pills {left:1.5rem;right:1.5rem;}
      .auth-pill {font-size:.7rem;}
      .auth-form-pane {padding:1rem;}
      .auth-nav {gap:.2rem;}
      .password-rules {grid-template-columns:1fr;}
      [data-testid="stSidebar"] {width: 100vw !important;}
    }
    @media (max-width: 380px) {
      .auth-promo h1 {font-size:2.45rem;}
      .auth-promo p {font-size:.88rem;}
      .auth-form-pane {padding:.8rem;}
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_secret(key: str) -> str | None:
    value = os.getenv(key)
    if value:
        return value
    try:
        value = st.secrets.get(key)
    except Exception:
        value = None
    return value


def safe(value: Any) -> str:
    return html.escape(str(value if value is not None else ""))


def normalize_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str):
        return [x.strip() for x in re.split(r",|\n", value) if x.strip()]
    return [str(value).strip()]


def youtube_search_url(meal_name: str, country: str) -> str:
    query = f"{meal_name} recipe {country}".strip()
    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"


def append_other(values: list[str], other: str) -> list[str]:
    final = [x for x in values if x and x != "Other"]
    if other.strip():
        final.append(other.strip())
    return final


def dedupe_keep_order(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        key = value.strip().lower()
        if key and key not in seen:
            seen.add(key)
            result.append(value.strip())
    return result


def extract_currency_code(label: str) -> str:
    return CURRENCY_CODE_BY_LABEL.get(label, label.split(" · ", 1)[0].strip())


def country_rows_for_continent(continent_code: str) -> list[tuple[str, str]]:
    rows = COUNTRIES_BY_CONTINENT.get(continent_code, [])
    return [(row.code, row.name) for row in rows]


def default_country_for(continent_code: str) -> str | None:
    for code, name in country_rows_for_continent(continent_code):
        if name == "Pakistan":
            return code
    rows = country_rows_for_continent(continent_code)
    return rows[0][0] if rows else None


def build_prompt(data: dict[str, Any]) -> str:
    restrictions = ", ".join(data["dietary_requirements"]) or "None specified"
    allergies = ", ".join(data["allergies"]) or "None specified"
    health = ", ".join(data["health_conditions"]) or "None specified"
    faith = data["faith_food_practice"] or "No specific faith-based food restriction"
    cuisine_regions = ", ".join(data["cuisine_regions"]) or "No specific regional cuisine selected"
    country_styles = ", ".join(data["country_cuisine_styles"][:12]) or "None"
    likes = ", ".join(data["liked_foods"]) or "No specific favorites"
    dislikes = ", ".join(data["disliked_foods"]) or "No specific dislikes"
    variety = ", ".join(data["variety_preferences"]) or "Balanced variety"
    fitness = ", ".join(data["fitness_focus"]) or "General wellness"

    return f"""
You are NourishAI, a cautious global nutrition and meal-planning assistant.
Generate a practical, culturally aware 7-day meal plan that follows the user's
explicit constraints. This is general wellness guidance, not medical care.

USER CONTEXT
Country / region: {data['country']}
Continent: {data['continent']}
Age: {data['age']}
Gender: {data['gender']}
Current weight: {data['weight']} {data['weight_unit']}
Target weight: {data['target_weight']} {data['weight_unit']}
Goal: {data['goal']}
Activity level: {data['activity_level']}
Training type: {data['training_type']}
Training days/week: {data['training_days_per_week']}
Workout timing: {data['workout_time']}
Fitness focus: {fitness}

DIET + FOOD CULTURE
Dietary requirements: {restrictions}
Food allergies (STRICT EXCLUSIONS): {allergies}
Faith / food-practice preference: {faith}
Preferred cuisine regions: {cuisine_regions}
Preferred country-inspired food styles: {country_styles}
Foods the user likes: {likes}
Foods the user dislikes: {dislikes}
Spice preference: {data['spice_preference']}
Meals per day: {data['meals_per_day']}

HEALTH + PRACTICALITY
Health considerations: {health}
Cooking time: {data['cooking_time']}
Kitchen access: {data['kitchen_access']}
Meal-prep style: {data['meal_prep_style']}

BUDGET + PLANNING
Budget amount: {data['currency']} {data['budget_amount']}
Budget cadence: {data['budget_frequency']}
Budget comfort: {data['budget_comfort']}
Variety preferences: {variety}

STRICT QUALITY + SAFETY RULES
1. Allergies are hard exclusions across the entire generated plan, including sauces, toppings, marinades,
   garnishes, substitutions, snacks, and optional swaps.
2. Respect every explicitly selected dietary requirement across the entire generated plan.
3. Use the user's selected faith/food-practice preference only as an explicit food rule; do not
   infer religious beliefs or add extra restrictions the user did not choose.
4. Never claim that a meal, product, restaurant, or ingredient is officially certified Halal or
   Kosher unless that certification is verified. Use phrases like "choose a certified option"
   when appropriate.
5. Health conditions are dietary considerations only. Never diagnose, prescribe medication,
   recommend treatment, or claim to cure or prevent a disease.
6. For kidney-related, pregnancy, breastfeeding, or similarly complex health contexts, use cautious
   wording and encourage professional review rather than giving disease-treatment instructions.
7. For muscle-building or gym goals, emphasize balanced meals and practical protein-rich foods,
   but do not prescribe drugs, steroids, or medical supplements.
8. Make meals culturally relevant and practical for the selected country/region while using the
   chosen cuisine preferences.
9. Budget is an estimate. Never claim live, exact, or guaranteed local food prices.
10. Prefer commonly available ingredients and avoid unnecessary repetition.
11. Use the selected activity level and training context to shape meal timing and food emphasis,
    without inventing clinical calorie or macro targets.
12. Follow the selected planning scope exactly. For per-meal, return one day containing exactly one meal. For per-day, return one day with the user's requested meal pattern. For per-week, return exactly 7 days. For per-month, return exactly 28 days representing a practical four-week plan.
13. Do not invent a direct YouTube video URL. Return recipe search text only.
14. Return JSON only and follow the supplied schema exactly.
""".strip()


MEAL_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "planning_notes": {"type": "string"},
        "days": {
            "type": "array",
            "minItems": 1,
            "maxItems": 28,
            "items": {
                "type": "object",
                "properties": {
                    "day": {"type": "integer"},
                    "theme": {"type": "string"},
                    "budget_fit": {
                        "type": "string",
                        "enum": ["within budget", "near budget", "may exceed"]
                    },
                    "day_note": {"type": "string"},
                    "meals": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 5,
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": ["Breakfast", "Lunch", "Dinner", "Snack"]
                                },
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "why_it_fits": {"type": "string"},
                                "dietary_considerations": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "prep_minutes": {"type": "integer"},
                                "recipe_search": {"type": "string"},
                            },
                            "required": [
                                "type",
                                "name",
                                "description",
                                "why_it_fits",
                                "dietary_considerations",
                                "prep_minutes",
                                "recipe_search",
                            ],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["day", "theme", "budget_fit", "day_note", "meals"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["summary", "planning_notes", "days"],
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
        max_completion_tokens=24000,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "nourishai_universal_adaptive_plan",
                "strict": True,
                "schema": MEAL_PLAN_SCHEMA,
            },
        },
        messages=[
            {
                "role": "system",
                "content": (
                    "You create concise, safe, structured meal plans. "
                    "Return only the JSON object matching the supplied schema."
                ),
            },
            {"role": "user", "content": build_prompt(data)},
        ],
    )

    content = response.choices[0].message.content or ""
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "The AI returned an unreadable plan. Please generate again."
        ) from exc

    if not isinstance(parsed, dict):
        raise ValueError("The AI returned an invalid plan object. Please generate again.")

    days = parsed.get("days")
    if not isinstance(days, list):
        raise ValueError("The AI returned an invalid plan. Please generate again.")

    scope = data.get("plan_scope", "Per week · 7 days")
    expected_days = {
        "Per meal · 1 meal": 1,
        "Per day · 1 day": 1,
        "Per week · 7 days": 7,
        "Per month · 28 days (4 weeks)": 28,
    }.get(scope, 7)

    if len(days) != expected_days:
        raise ValueError(
            f"The AI returned {len(days)} days, but the selected scope requires {expected_days}. Please generate again."
        )

    for index, day in enumerate(days, start=1):
        day["day"] = index
        meals = day.get("meals", [])
        minimum_meals = 1 if scope == "Per meal · 1 meal" else 3
        if len(meals) < minimum_meals:
            raise ValueError(f"Day {index} is missing required meals for the selected scope. Please generate again.")
        if scope == "Per meal · 1 meal" and len(meals) != 1:
            day["meals"] = meals[:1]
        for meal in day.get("meals", []):
            if int(meal.get("prep_minutes", 0)) < 0:
                meal["prep_minutes"] = 0

    return parsed


def validate_inputs(age: int, weight: float, target_weight: float, height: float, budget: float) -> str | None:
    if not 18 <= age <= 100:
        return "Please enter an age between 18 and 100."
    if weight <= 0 or target_weight <= 0 or height <= 0:
        return "Weight, target weight, and height must be greater than zero."
    if budget <= 0:
        return "Budget must be greater than zero."
    return None


def plan_as_text(plan: dict[str, Any], meta: dict[str, Any]) -> str:
    lines = [
        APP_NAME,
        f"Universal {meta.get('plan_scope', 'adaptive')} meal plan",
        "=" * 38,
        "",
        plan.get("summary", ""),
        plan.get("planning_notes", ""),
        "",
        (
            f"Context: {meta.get('country', '')} · {meta.get('currency', '')} "
            f"{meta.get('budget_amount', '')} {meta.get('budget_frequency', '')}"
        ),
        f"Goal: {meta.get('goal', '')} · Activity: {meta.get('activity_level', '')}",
        "",
    ]

    for day in plan.get("days", []):
        lines.append(
            f"DAY {day.get('day', '')} · {day.get('theme', '')} · {day.get('budget_fit', '').title()}"
        )
        if day.get("day_note"):
            lines.append(f"Note: {day.get('day_note')}")
        for meal in day.get("meals", []):
            lines.append(f"{meal.get('type', '')}: {meal.get('name', '')}")
            lines.append(f"  {meal.get('description', '')}")
            lines.append(f"  Why it fits: {meal.get('why_it_fits', '')}")
            if meal.get("prep_minutes") is not None:
                lines.append(f"  Prep: {meal.get('prep_minutes')} minutes")
        lines.append("")

    lines.append("Safety note: " + DISCLAIMER)
    return "\n".join(lines)


def render_meal(meal: dict[str, Any], country: str) -> None:
    name = safe(meal.get("name", "Meal"))
    desc = safe(meal.get("description", ""))
    why = safe(meal.get("why_it_fits", ""))
    meal_type = safe(meal.get("type", "Meal"))
    prep = safe(meal.get("prep_minutes", ""))
    tags = "".join(
        f"<span class='tag'>{safe(item)}</span>"
        for item in normalize_list(meal.get("dietary_considerations"))[:6]
    )
    search = str(meal.get("recipe_search") or meal.get("name") or "recipe")
    recipe_url = youtube_search_url(search, country)

    st.markdown(
        f"""
        <div class="meal">
          <div class="meal-type">{meal_type} · {prep} min</div>
          <div class="meal-name">{name}</div>
          <div class="meal-desc">{desc}</div>
          <div class="micro" style="margin-top:.5rem;"><b>Why it fits:</b> {why}</div>
          <div>{tags}</div>
          <div class="recipe-box">
            <div class="micro">🎥 Recipe search · no fabricated video URLs</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.link_button(
        "▶ Find a recipe",
        recipe_url,
        use_container_width=True,
    )



# ---------------------------------------------------------------------------
# Authentication, persistence & document export
# ---------------------------------------------------------------------------
initialize_database()


def current_user() -> dict[str, Any] | None:
    return st.session_state.get("user")


def logout() -> None:
    for key in ["user", "plan", "profile_meta", "saved_plan_id", "view", "auth_page"]:
        st.session_state.pop(key, None)
    st.session_state.auth_page = "Sign in"
    _flash("success", "You have signed out successfully.")
    st.rerun()


def password_policy_message() -> str:
    return "Use at least 8 characters with an uppercase letter, lowercase letter, number, and special character."


def send_reset_email(email: str, code: str) -> bool:
    host = get_secret("SMTP_HOST")
    user = get_secret("SMTP_USER")
    password = get_secret("SMTP_PASSWORD")
    sender = get_secret("SMTP_FROM") or user
    port = int(get_secret("SMTP_PORT") or "587")
    if not (host and user and password and sender):
        return False
    msg = EmailMessage()
    msg["Subject"] = "NourishAI password reset code"
    msg["From"] = sender
    msg["To"] = email
    msg.set_content(
        f"Your NourishAI password reset code is {code}. It expires in 30 minutes. "
        "If you did not request this, ignore this message."
    )
    try:
        with smtplib.SMTP(host, port, timeout=15) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
        return True
    except Exception:
        return False


def build_docx(plan: dict[str, Any], meta: dict[str, Any]) -> bytes:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.6)
    section.bottom_margin = Inches(0.6)
    section.left_margin = Inches(0.7)
    section.right_margin = Inches(0.7)

    styles = doc.styles
    styles["Normal"].font.name = "Aptos"
    styles["Normal"].font.size = Pt(10)
    styles["Title"].font.name = "Aptos Display"
    styles["Title"].font.size = Pt(24)
    styles["Title"].font.bold = True
    styles["Heading 1"].font.name = "Aptos Display"
    styles["Heading 1"].font.size = Pt(16)
    styles["Heading 1"].font.bold = True
    styles["Heading 2"].font.name = "Aptos Display"
    styles["Heading 2"].font.size = Pt(13)
    styles["Heading 2"].font.bold = True

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("NourishAI")
    run.bold = True
    run.font.size = Pt(26)
    run.font.color.rgb = RGBColor(8, 119, 105)

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = subtitle.add_run(f"Personalized {meta.get('plan_scope', 'Adaptive')} Meal Plan")
    r.bold = True
    r.font.size = Pt(15)
    subtitle.add_run(f"\nGenerated {datetime.now().strftime('%d %b %Y, %H:%M')}")

    doc.add_heading("Plan Overview", level=1)
    doc.add_paragraph(plan.get("summary", "Your personalized plan."))
    if plan.get("planning_notes"):
        p = doc.add_paragraph()
        r = p.add_run("Planner notes: ")
        r.bold = True
        p.add_run(plan.get("planning_notes", ""))

    table = doc.add_table(rows=0, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Light Shading Accent 1"
    profile_rows = [
        ("Country / Region", meta.get("country", "Global")),
        ("Goal", meta.get("goal", "")),
        ("Plan scope", meta.get("plan_scope", "Adaptive")),
        ("Activity", meta.get("activity_level", "")),
        ("Fitness focus", ", ".join(meta.get("fitness_focus", []))),
        ("Dietary requirements", ", ".join(meta.get("dietary_requirements", []))),
        ("Allergies", ", ".join(meta.get("allergies", []))),
        ("Food-practice preference", meta.get("faith_food_practice", "")),
        ("Cuisine", ", ".join(meta.get("cuisines", []))),
        ("Budget", f"{meta.get('currency', '')} {meta.get('budget_amount', '')} · {meta.get('budget_frequency', '')}"),
    ]
    for label, value in profile_rows:
        cells = table.add_row().cells
        cells[0].text = str(label)
        cells[1].text = str(value)
        cells[0].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        cells[1].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

    for day in plan.get("days", []):
        doc.add_page_break()
        doc.add_heading(f"Day {day.get('day')} · {day.get('theme', 'Personalized day')}", level=1)
        if day.get("day_note"):
            doc.add_paragraph(day.get("day_note", ""))
        for meal in day.get("meals", []):
            doc.add_heading(f"{meal.get('type', 'Meal')} · {meal.get('name', 'Meal')}", level=2)
            doc.add_paragraph(meal.get("description", ""))
            p = doc.add_paragraph()
            rr = p.add_run("Why it fits: ")
            rr.bold = True
            p.add_run(meal.get("why_it_fits", ""))
            p = doc.add_paragraph()
            rr = p.add_run("Prep time: ")
            rr.bold = True
            p.add_run(f"{meal.get('prep_minutes', '')} minutes")
            tags = meal.get("dietary_considerations", [])
            if tags:
                p = doc.add_paragraph()
                rr = p.add_run("Considerations: ")
                rr.bold = True
                p.add_run(", ".join(tags))
            p = doc.add_paragraph()
            rr = p.add_run("Recipe search: ")
            rr.bold = True
            p.add_run(youtube_search_url(meal.get("recipe_search") or meal.get("name", "recipe"), meta.get("country", "")))

    doc.add_page_break()
    doc.add_heading("Health & Safety", level=1)
    doc.add_paragraph(DISCLAIMER)
    doc.add_paragraph("Budget figures are planning estimates, not live or guaranteed market prices.")

    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()


def _flash(kind: str, message: str) -> None:
    st.session_state.flash = {"kind": kind, "message": message}


def render_flash() -> None:
    flash = st.session_state.pop("flash", None)
    if not flash:
        return
    cls = "flash-success" if flash.get("kind") == "success" else "flash-error"
    icon = "✓" if flash.get("kind") == "success" else "!"
    st.markdown(
        f"<div class='{cls}'><b>{icon}</b>&nbsp; {safe(flash.get('message',''))}</div>",
        unsafe_allow_html=True,
    )


def password_rules_html(password: str) -> str:
    checks = [
        ("8+ characters", len(password) >= 8),
        ("Uppercase letter", any(c.isupper() for c in password)),
        ("Lowercase letter", any(c.islower() for c in password)),
        ("Number", any(c.isdigit() for c in password)),
        ("Special character", any(not c.isalnum() for c in password)),
    ]
    parts = []
    for label, ok in checks:
        parts.append(f"<div class='{'rule-ok' if ok else 'rule-off'}'>{'✓' if ok else '○'} {safe(label)}</div>")
    return "<div class='password-rules'>" + "".join(parts) + "</div>"


def render_auth() -> None:
    if "auth_page" not in st.session_state:
        st.session_state.auth_page = "Sign in"
    page = st.session_state.auth_page
    render_flash()

    promo_col, form_col = st.columns([1.08, 0.92], gap="large")
    with promo_col:
        st.markdown(
            """
            <section class='auth-promo' style='min-height:610px;border-radius:32px;'>
              <div class='mini-logo'>
                <div class='mini-logo-mark'>🥗</div>
                <div><b>NourishAI</b><br><small style='color:rgba(255,255,255,.7)'>Universal nutrition studio</small></div>
              </div>
              <h1>Eat well.<br>Live your way.</h1>
              <p>Plan around the person, not the template — goals, culture, allergies, food rules, health context, fitness routine and budget.</p>
              <div style='margin-top:1.35rem;display:grid;gap:.65rem;position:relative;z-index:2;'>
                <div class='auth-pill'>✦ AI-personalized 7-day plans</div>
                <div class='auth-pill'>🌍 Global cuisines, regions and currencies</div>
                <div class='auth-pill'>🛡 Strict allergy & dietary constraints</div>
                <div class='auth-pill'>📚 Save, revisit and export plans</div>
              </div>
              <div style='position:absolute;right:8%;bottom:17%;width:130px;height:130px;border-radius:50%;background:radial-gradient(circle at 30% 25%,#f4ffbc,#8ae48a 22%,rgba(16,165,143,.08) 55%);box-shadow:0 0 0 16px rgba(255,255,255,.06),0 0 0 34px rgba(255,255,255,.035);animation:float 5.5s ease-in-out infinite;'></div>
            </section>
            """,
            unsafe_allow_html=True,
        )

    with form_col:
        st.markdown(
            "<div class='auth-eyebrow'>NourishAI account</div><div class='auth-heading'>Your plan, your space.</div><div class='auth-copy'>Sign in to continue, or create a free account to save meal plans and build a private nutrition history.</div>",
            unsafe_allow_html=True,
        )
        nav = st.columns(2)
        with nav[0]:
            if st.button("Sign in", key="authnav_signin", use_container_width=True, type="primary" if page == "Sign in" else "secondary"):
                st.session_state.auth_page = "Sign in"
                st.rerun()
        with nav[1]:
            if st.button("Create account", key="authnav_register", use_container_width=True, type="primary" if page == "Register" else "secondary"):
                st.session_state.auth_page = "Register"
                st.rerun()

        if page == "Sign in":
            with st.form("sign_in_form", clear_on_submit=False):
                email = st.text_input("Email address", placeholder="you@example.com", key="signin_email")
                password = st.text_input("Password", type="password", placeholder="Enter your password", key="signin_password")
                submitted = st.form_submit_button("Sign in →", type="primary", use_container_width=True)
            st.markdown("<div class='auth-help'>Use the email you registered with.</div>", unsafe_allow_html=True)
            if st.button("Forgot password?", key="goto_forgot", use_container_width=False):
                st.session_state.auth_page = "Forgot password"
                st.rerun()
            if submitted:
                if not email.strip() or not password:
                    st.error("Please enter both your email address and password.")
                else:
                    user = authenticate_user(email, password)
                    if not user:
                        st.error("Email or password is incorrect. Check your details and try again.")
                    else:
                        st.session_state.user = user
                        st.session_state.view = "planner"
                        _flash("success", f"Welcome back, {user['name']}. Your workspace is ready.")
                        st.rerun()

        elif page == "Register":
            with st.form("register_form", clear_on_submit=False):
                name = st.text_input("Full name", placeholder="Muhammad Rayyan Bhatti", key="register_name")
                email = st.text_input("Email address", placeholder="you@example.com", key="register_email")
                c1, c2 = st.columns(2)
                with c1:
                    password = st.text_input("Password", type="password", placeholder="Create a strong password", key="register_password")
                with c2:
                    confirm = st.text_input("Confirm password", type="password", placeholder="Repeat password", key="register_confirm")
                st.markdown(password_rules_html(password), unsafe_allow_html=True)
                submitted = st.form_submit_button("Create account →", type="primary", use_container_width=True)
            if submitted:
                if not name.strip():
                    st.error("Please enter your full name.")
                elif not email.strip() or "@" not in email or "." not in email.split("@")[-1]:
                    st.error("Please enter a valid email address.")
                elif not validate_password_strength(password):
                    st.error("Password does not meet all the requirements shown above.")
                elif password != confirm:
                    st.error("Passwords do not match. Re-enter the same password in both fields.")
                else:
                    try:
                        user = create_user(name, email, password)
                        st.session_state.user = user
                        st.session_state.view = "planner"
                        _flash("success", "Account created successfully. Welcome to NourishAI!")
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))

        else:  # Forgot password
            st.info("Enter your account email to receive a short-lived reset code. Configure SMTP for real email delivery; otherwise a demo code is shown for the hackathon.")
            with st.form("forgot_form", clear_on_submit=False):
                email = st.text_input("Account email", placeholder="you@example.com", key="forgot_email")
                submitted = st.form_submit_button("Create reset code", type="primary", use_container_width=True)
            if submitted:
                if not email.strip():
                    st.error("Please enter your account email.")
                else:
                    result = create_reset_request(email)
                    if result:
                        code = result["code"]
                        expires = result["expires_at"]
                        sent = send_reset_email(email.strip().lower(), code)
                        st.session_state.reset_email = email.strip().lower()
                        st.session_state.reset_ready = True
                        if sent:
                            st.success("If the account exists, a reset code has been sent to the configured email address.")
                        else:
                            st.success(f"Demo reset code: {code}. It expires at {expires} UTC.")
                    else:
                        st.success("If the account exists, a reset code has been generated.")
            if st.session_state.get("reset_ready"):
                st.markdown("<div class='auth-eyebrow' style='margin-top:1rem'>Reset your password</div>", unsafe_allow_html=True)
                with st.form("reset_form", clear_on_submit=False):
                    reset_email = st.text_input("Email address", value=st.session_state.get("reset_email", ""), key="reset_email_field")
                    code = st.text_input("Reset code", placeholder="8-digit code", key="reset_code")
                    c1, c2 = st.columns(2)
                    with c1:
                        new_password = st.text_input("New password", type="password", placeholder="Create a new password", key="reset_password")
                    with c2:
                        confirm = st.text_input("Confirm new password", type="password", placeholder="Repeat new password", key="reset_confirm")
                    st.markdown(password_rules_html(new_password), unsafe_allow_html=True)
                    reset_submitted = st.form_submit_button("Set new password →", type="primary", use_container_width=True)
                if reset_submitted:
                    if not reset_email.strip() or not code.strip():
                        st.error("Enter your email address and reset code.")
                    elif not validate_password_strength(new_password):
                        st.error("Password does not meet all the requirements shown above.")
                    elif new_password != confirm:
                        st.error("Passwords do not match.")
                    else:
                        reset = get_reset_request(reset_email.strip().lower(), code.strip())
                        if not reset:
                            st.error("Invalid or expired reset code. Request a new code and try again.")
                        else:
                            update_password(reset["user_id"], new_password)
                            mark_reset_used(reset["id"])
                            _flash("success", "Password updated successfully. Sign in with your new password.")
                            st.session_state.auth_page = "Sign in"
                            st.session_state.reset_ready = False
                            st.rerun()


def render_settings() -> None:
    user = current_user()
    render_flash()
    st.markdown(
        "<div class='section-kicker'>Account</div><div class='section-title'>Settings & security</div><div class='section-sub'>Manage your account details and change your password without leaving NourishAI.</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='settings-card'><div class='micro'>SIGNED IN AS</div><div style='font-size:1.2rem;font-weight:800;margin-top:.25rem'>{safe(user['name'])}</div><div class='auth-help'>{safe(user['email'])}</div></div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)
    with st.expander("🔐 Change password", expanded=True):
        with st.form("change_password_form", clear_on_submit=False):
            current = st.text_input("Current password", type="password", key="current_password")
            new_pw = st.text_input("New password", type="password", key="settings_new_password")
            confirm = st.text_input("Confirm new password", type="password", key="settings_confirm_password")
            st.markdown(password_rules_html(new_pw), unsafe_allow_html=True)
            submitted = st.form_submit_button("Update password", type="primary", use_container_width=True)
        if submitted:
            if not authenticate_user(user["email"], current):
                st.error("Current password is incorrect.")
            elif not validate_password_strength(new_pw):
                st.error("Password does not meet all the requirements shown above.")
            elif new_pw != confirm:
                st.error("Passwords do not match.")
            else:
                update_password(user["id"], new_pw)
                _flash("success", "Your password was changed successfully.")
                st.rerun()

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    with st.expander("ℹ️ Account and data", expanded=False):
        st.write("Your saved meal plans are isolated to your account. Passwords are stored as salted scrypt hashes. This hackathon build uses SQLite persistence; a production deployment should move account data to managed PostgreSQL or another server-side database.")

def render_history() -> None:
    user = current_user()
    st.markdown("<div class='section-kicker'>Saved plans</div><div class='section-title'>Your nutrition history</div><div class='section-sub'>Plans belong to your account, so another user cannot see them.</div>", unsafe_allow_html=True)
    plans = list_saved_plans(user["id"])
    if not plans:
        st.info("No saved plans yet. Generate a plan and choose ‘Save to history’ to keep it here.")
        return
    for item in plans:
        c1, c2, c3 = st.columns([5, 1.3, 1.3])
        with c1:
            st.markdown(f"**{safe(item['title'])}**")
            st.caption(f"{item['created_at']} · {item['country']} · {item['goal']}")
        with c2:
            if st.button("Open", key=f"open_{item['id']}", use_container_width=True):
                loaded = get_saved_plan(item["id"], user["id"])
                if loaded:
                    st.session_state.plan = loaded["plan"]
                    st.session_state.profile_meta = loaded["meta"]
                    st.session_state.saved_plan_id = item["id"]
                    st.session_state.view = "planner"
                    st.rerun()
        with c3:
            if st.button("Delete", key=f"del_{item['id']}", use_container_width=True):
                delete_saved_plan(item["id"], user["id"])
                st.rerun()
        st.divider()

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "plan" not in st.session_state:
    st.session_state.plan = None
if "profile_meta" not in st.session_state:
    st.session_state.profile_meta = None
if "view" not in st.session_state:
    st.session_state.view = "planner"
if "auth_page" not in st.session_state:
    st.session_state.auth_page = "Sign in"
if current_user() is None:
    render_auth()
    st.stop()



if st.session_state.view in {"history", "settings"}:
    st.sidebar.markdown(f"### {safe(current_user()['name'])}")
    st.sidebar.caption(safe(current_user()['email']))
    if st.sidebar.button("← Back to planner", use_container_width=True):
        st.session_state.view = "planner"
        st.rerun()
    if st.sidebar.button("🗂 History", use_container_width=True):
        st.session_state.view = "history"
        st.rerun()
    if st.sidebar.button("⚙ Settings", use_container_width=True):
        st.session_state.view = "settings"
        st.rerun()
    if st.sidebar.button("↗ Sign out", use_container_width=True):
        logout()
    if st.session_state.view == "history":
        render_history()
    else:
        render_settings()
    st.stop()

render_flash()
st.sidebar.markdown(f"### {safe(current_user()['name'])}")
st.sidebar.caption(safe(current_user()['email']))
if st.sidebar.button("🗂 History", use_container_width=True):
    st.session_state.view = "history"
    st.rerun()
if st.sidebar.button("⚙ Settings", use_container_width=True):
    st.session_state.view = "settings"
    st.rerun()
if st.sidebar.button("↗ Sign out", use_container_width=True):
    logout()

# ---------------------------------------------------------------------------
# Header / hero
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="topbar">
      <div class="brand">
        <div class="brand-mark">🥗</div>
        <div>
          <div class="brand-name">{APP_NAME}</div>
          <div class="brand-meta">AI nutrition studio · universal edition</div>
        </div>
      </div>
      <div class="version-badge">● Live build · {VERSION}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <section class="hero">
      <div class="hero-grid">
        <div>
          <div class="eyebrow">Global nutrition · personal context · practical planning</div>
          <h1>Eat like you.<br>anywhere.</h1>
          <div class="hero-copy">
            {TAGLINE}
            Build the right planning scope around your goal, activity, food culture, dietary requirements,
            allergies, faith-based food practices, health considerations, cooking reality, and budget.
          </div>
          <div class="hero-pills">
            <span class="hero-pill">✦ Meal, day, week & month planning</span>
            <span class="hero-pill">◌ Global cuisines & food styles</span>
            <span class="hero-pill">⌁ Strict allergy exclusions</span>
            <span class="hero-pill">◍ Gym & performance aware</span>
            <span class="hero-pill">✺ Budget across multiple cadences</span>
          </div>
        </div>
        <div class="orb"><span></span></div>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="feature-strip">
      <div class="feature-card">
        <div class="feature-emoji">🌍</div>
        <div class="feature-title">Built for everywhere</div>
        <div class="feature-copy">Countries, regions, currencies and food cultures across the world.</div>
      </div>
      <div class="feature-card">
        <div class="feature-emoji">🏋️</div>
        <div class="feature-title">Fitness-aware</div>
        <div class="feature-copy">Muscle-building, strength, endurance, recovery and gym routines.</div>
      </div>
      <div class="feature-card">
        <div class="feature-emoji">🛡️</div>
        <div class="feature-title">Constraint-first</div>
        <div class="feature-copy">Allergies stay hard exclusions; explicit dietary rules remain consistent.</div>
      </div>
      <div class="feature-card">
        <div class="feature-emoji">✨</div>
        <div class="feature-title">Practical output</div>
        <div class="feature-copy">Seven days of meals with prep time, rationale and recipe search.</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Input experience
# ---------------------------------------------------------------------------
if st.session_state.plan is None:
    st.markdown(
        """
        <div class="section-head">
          <div class="section-kicker">Design your week</div>
          <div class="section-title">Tell NourishAI what “fits” actually means.</div>
          <div class="section-sub">
            The form is intentionally guided: personal context first, then food and health preferences,
            then fitness, budget and planning style.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("universal_profile_form", clear_on_submit=False):
        tab1, tab2, tab3, tab4 = st.tabs(
            ["🌍 Goal & profile", "🥑 Food & culture", "🏋️ Health & fitness", "💳 Budget & planning"]
        )

        with tab1:
            st.markdown(
                '<div class="tab-caption">Start with the outcome you want and the context you live in.</div>',
                unsafe_allow_html=True,
            )
            a1, a2 = st.columns(2)

            with a1:
                continent_labels = ["All continents"] + [
                    CONTINENT_LABELS[c] for c in CONTINENT_ORDER
                ]
                default_continent = "🌏 Asia"
                selected_continent_label = st.selectbox(
                    "Continent",
                    continent_labels,
                    index=continent_labels.index(default_continent),
                    help="Used to organize the complete country/region list.",
                )

                continent_code = "ALL"
                for code, label in CONTINENT_LABELS.items():
                    if label == selected_continent_label:
                        continent_code = code
                        break

                if continent_code == "ALL":
                    country_choices = sorted(
                        [(code, row.name) for code, row in COUNTRY_ROW_BY_CODE.items() if code != "XK"],
                        key=lambda x: x[1].lower(),
                    )
                    default_country_name = "Pakistan"
                else:
                    country_choices = [
                        (row.code, row.name)
                        for row in COUNTRIES_BY_CONTINENT.get(continent_code, [])
                    ]
                    default_country_name = "Pakistan" if any(
                        name == "Pakistan" for _, name in country_choices
                    ) else (country_choices[0][1] if country_choices else "")

                country_names = [name for _, name in country_choices]
                default_country_index = (
                    country_names.index(default_country_name)
                    if default_country_name in country_names
                    else 0
                )
                country = st.selectbox(
                    "Country / region",
                    country_names,
                    index=default_country_index if country_names else 0,
                    help="The country list is grouped through the continent selector and includes ISO-listed countries and territories.",
                )

                selected_country_code = next(
                    (code for code, name in country_choices if name == country),
                    "PK",
                )
                selected_country_row = COUNTRY_ROW_BY_CODE.get(selected_country_code)

                gender = st.radio(
                    "Gender",
                    ["Female", "Male", "Non-binary / Prefer not to say"],
                    horizontal=True,
                )

                age = st.number_input(
                    "Age",
                    min_value=18,
                    max_value=100,
                    value=24,
                    step=1,
                )

            with a2:
                goal = st.selectbox(
                    "Primary goal",
                    GOALS,
                    index=0,
                )

                unit_system = st.radio(
                    "Measurement system",
                    ["Metric", "Imperial"],
                    horizontal=True,
                )

                if unit_system == "Metric":
                    weight = st.number_input(
                        "Current weight (kg)",
                        min_value=1.0,
                        value=65.0,
                        step=0.5,
                    )
                    target_weight = st.number_input(
                        "Target weight (kg)",
                        min_value=1.0,
                        value=60.0,
                        step=0.5,
                    )
                    height = st.number_input(
                        "Height (cm)",
                        min_value=1.0,
                        value=170.0,
                        step=0.5,
                    )
                else:
                    weight = st.number_input(
                        "Current weight (lb)",
                        min_value=1.0,
                        value=143.0,
                        step=0.5,
                    )
                    target_weight = st.number_input(
                        "Target weight (lb)",
                        min_value=1.0,
                        value=132.0,
                        step=0.5,
                    )
                    height = st.number_input(
                        "Height (in)",
                        min_value=1.0,
                        value=67.0,
                        step=0.5,
                    )

                st.markdown(
                    """
                    <div class="soft-note">
                      🎯 The target is used as planning context. NourishAI does not calculate calories,
                      prescribe weight-loss rates, or make clinical weight recommendations.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with tab2:
            st.markdown(
                '<div class="tab-caption">Tell us what you eat, avoid, enjoy, and observe.</div>',
                unsafe_allow_html=True,
            )

            b1, b2 = st.columns(2)

            with b1:
                dietary_requirements = st.multiselect(
                    "Dietary requirements",
                    DIETARY_REQUIREMENTS,
                    help="Broad dietary styles plus medical-adjacent food patterns such as low-sodium or gluten-free. These are planning preferences, not treatment plans.",
                )
                other_dietary = st.text_input(
                    "Other dietary requirement",
                    placeholder="Type any additional dietary rule",
                )

                allergies = st.multiselect(
                    "Food allergies · strict exclusions",
                    ALLERGIES,
                    help="All selected allergies are treated as hard exclusions across the entire plan.",
                )
                other_allergy = st.text_input(
                    "Other allergy",
                    placeholder="Type another allergy if not listed",
                )

                faith_food_practice = st.selectbox(
                    "Faith / food-practice preference",
                    FAITH_FOOD_PRACTICES,
                )
                other_food_practice = st.text_input(
                    "Other faith / food-practice preference",
                    placeholder="Optional",
                )

            with b2:
                cuisine_regions = st.multiselect(
                    "Preferred cuisine regions",
                    CUISINE_REGIONS,
                    help="Regional and country-style cuisine families.",
                )
                country_cuisine_styles = st.multiselect(
                    "Country-inspired cuisines",
                    COUNTRY_INSPIRED_CUISINES,
                    help="Country-inspired styles for global coverage. Select one or more.",
                )
                other_cuisine = st.text_input(
                    "Other cuisine or food tradition",
                    placeholder="Type another cuisine or food tradition",
                )

                spice_preference = st.select_slider(
                    "Spice preference",
                    options=["Very mild", "Mild", "Balanced", "Spicy", "Very spicy"],
                    value="Balanced",
                )

                liked_foods = st.multiselect(
                    "Foods you like",
                    COMMON_FOODS,
                )
                liked_foods_other = st.text_input(
                    "Other foods you like",
                    placeholder="e.g. salmon, quinoa, biryani",
                )

                disliked_foods = st.multiselect(
                    "Foods you dislike / prefer to avoid",
                    COMMON_FOODS,
                )
                disliked_foods_other = st.text_input(
                    "Other foods you dislike",
                    placeholder="e.g. mushrooms, olives",
                )

        with tab3:
            st.markdown(
                '<div class="tab-caption">Add the lifestyle and health context that should shape meal choices.</div>',
                unsafe_allow_html=True,
            )

            c1, c2 = st.columns(2)

            with c1:
                health_considerations = st.multiselect(
                    "Health considerations",
                    HEALTH_CONSIDERATIONS,
                    help="These are planning considerations only. They do not turn the app into a diagnostic or treatment tool.",
                )
                other_health = st.text_input(
                    "Other health consideration",
                    placeholder="Type another consideration if needed",
                )

                activity_level = st.selectbox(
                    "Activity level",
                    ACTIVITY_LEVELS,
                )

                fitness_focus = st.multiselect(
                    "Fitness / gym focus",
                    FITNESS_FOCUSES,
                    default=["General wellness"],
                )

            with c2:
                training_type = st.selectbox(
                    "Training type",
                    TRAINING_TYPES,
                )
                training_days_per_week = st.number_input(
                    "Training days per week",
                    min_value=0,
                    max_value=14,
                    value=3,
                    step=1,
                )
                workout_time = st.selectbox(
                    "Typical workout timing",
                    WORKOUT_TIMES,
                )
                meals_per_day = st.selectbox(
                    "Meals per day",
                    [3, 4, 5],
                    index=1,
                )

                st.markdown(
                    """
                    <div class="soft-note">
                      🏋️ Gym mode is nutrition-planning support: balanced meals, practical protein-rich
                      foods and timing ideas. No steroids, drug advice, or clinical supplement prescriptions.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with tab4:
            st.markdown(
                '<div class="tab-caption">Make the plan realistic enough that you would actually follow it.</div>',
                unsafe_allow_html=True,
            )

            d1, d2, d3 = st.columns(3)

            with d1:
                country_currency_codes = (
                    selected_country_row.currency_codes
                    if selected_country_row and selected_country_row.currency_codes
                    else ("USD",)
                )

                default_currency_label = next(
                    (
                        label
                        for label, code in CURRENCY_CODE_BY_LABEL.items()
                        if code == country_currency_codes[0]
                    ),
                    CURRENCY_OPTIONS[0] if CURRENCY_OPTIONS else "USD",
                )

                currency = st.selectbox(
                    "Planning currency",
                    CURRENCY_OPTIONS,
                    index=CURRENCY_OPTIONS.index(default_currency_label)
                    if default_currency_label in CURRENCY_OPTIONS
                    else 0,
                    help="Country-based default with the ability to choose any supported currency.",
                )

                budget_amount = st.number_input(
                    "Budget amount",
                    min_value=1.0,
                    value=100.0,
                    step=5.0,
                )

                budget_frequency = st.selectbox(
                    "Budget frequency",
                    BUDGET_FREQUENCIES,
                )

                budget_comfort = st.selectbox(
                    "Budget comfort",
                    ["Low", "Medium", "Flexible"],
                    index=1,
                )

            with d2:
                plan_scope = st.selectbox(
                    "Plan generation scope",
                    PLAN_SCOPES,
                    index=2,
                    help="Choose whether NourishAI should prepare a single meal, one day, a week, or a 4-week monthly plan.",
                )

                variety_preferences = st.multiselect(
                    "Variety preferences",
                    VARIETY_OPTIONS,
                    default=["Balanced variety"],
                )

                meal_prep_style = st.selectbox(
                    "Meal-prep style",
                    ["Cook fresh most days", "Meal prep 2–3 times/week", "Batch cook", "Mix of fresh + prep"],
                )

                cooking_time = st.selectbox(
                    "Typical cooking time",
                    COOKING_TIME_OPTIONS,
                )

                kitchen_access = st.selectbox(
                    "Kitchen access",
                    KITCHEN_OPTIONS,
                )

            with d3:
                st.markdown(
                    """
                    <div class="glass" style="padding:.95rem;">
                      <div style="font-weight:800;font-size:.88rem;">What gets optimized</div>
                      <div class="hint" style="margin-top:.4rem;">
                        • Food constraints first<br>
                        • Allergies as hard exclusions<br>
                        • Culture and local practicality<br>
                        • Activity + fitness context<br>
                        • Budget and preparation reality<br>
                        • Planning scope: meal → day → week → month
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                    <div class="safety" style="margin-top:.75rem;">
                      🛡️ <b>Health & safety</b><br>{safe(DISCLAIMER)}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown('<div class="cta-panel">', unsafe_allow_html=True)
        scope_button_labels = {
            "Per meal · 1 meal": "✨ Generate my personalized meal",
            "Per day · 1 day": "✨ Generate my personalized day",
            "Per week · 7 days": "✨ Generate my personalized week",
            "Per month · 28 days (4 weeks)": "✨ Generate my personalized month",
        }
        submitted = st.form_submit_button(
            scope_button_labels.get(plan_scope, "✨ Generate my personalized plan"),
            type="primary",
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        error = validate_inputs(age, weight, target_weight, height, budget_amount)
        if error:
            st.error(error)
            st.stop()

        continent_name = (
            CONTINENT_LABELS.get(continent_code, "🌐 Global")
            if continent_code != "ALL"
            else "🌐 Global"
        )

        dietary_final = append_other(dietary_requirements, other_dietary)
        allergies_final = append_other(allergies, other_allergy)
        health_final = append_other(health_considerations, other_health)
        food_practice_final = faith_food_practice
        if other_food_practice.strip():
            food_practice_final = f"{faith_food_practice}; {other_food_practice.strip()}"

        cuisines_final = append_other(cuisine_regions, other_cuisine)
        if country_cuisine_styles:
            cuisines_final.extend(country_cuisine_styles)
        cuisines_final = dedupe_keep_order(cuisines_final)

        liked_final = dedupe_keep_order(liked_foods + ([liked_foods_other.strip()] if liked_foods_other.strip() else []))
        disliked_final = dedupe_keep_order(disliked_foods + ([disliked_foods_other.strip()] if disliked_foods_other.strip() else []))

        if not cuisines_final:
            cuisines_final = [f"{country} · country-inspired"]

        if not dietary_final:
            dietary_final = ["No special dietary requirement"]

        if "None / no specific consideration" in health_final and len(health_final) > 1:
            health_final = [x for x in health_final if x != "None / no specific consideration"]
        elif not health_final:
            health_final = ["None stated"]

        selected_currency_code = extract_currency_code(currency)

        profile = {
            "country": country,
            "continent": continent_name,
            "age": age,
            "gender": gender,
            "weight": weight,
            "target_weight": target_weight,
            "height": height,
            "weight_unit": "kg" if unit_system == "Metric" else "lb",
            "height_unit": "cm" if unit_system == "Metric" else "in",
            "goal": goal,
            "dietary_requirements": dietary_final,
            "allergies": allergies_final,
            "faith_food_practice": food_practice_final,
            "cuisines": cuisines_final,
            "cuisine_regions": cuisines_final,
            "country_cuisine_styles": country_cuisine_styles,
            "health_conditions": health_final,
            "activity_level": activity_level,
            "fitness_focus": fitness_focus,
            "training_type": training_type,
            "training_days_per_week": training_days_per_week,
            "workout_time": workout_time,
            "meals_per_day": meals_per_day,
            "liked_foods": liked_final,
            "disliked_foods": disliked_final,
            "spice_preference": spice_preference,
            "currency": selected_currency_code,
            "budget_amount": budget_amount,
            "budget_frequency": budget_frequency,
            "plan_scope": plan_scope,
            "plan_scope_rules": {
                "Per meal · 1 meal": "Return exactly 1 day containing exactly 1 meal.",
                "Per day · 1 day": "Return exactly 1 day with breakfast, lunch and dinner; add a snack if appropriate.",
                "Per week · 7 days": "Return exactly 7 days with breakfast, lunch and dinner; add snacks when appropriate.",
                "Per month · 28 days (4 weeks)": "Return exactly 28 days grouped conceptually as four practical weeks, with breakfast, lunch and dinner; add snacks when appropriate.",
            }.get(plan_scope, "Return a practical plan for the selected scope."),
            "budget_comfort": budget_comfort,
            "variety_preferences": variety_preferences,
            "meal_prep_style": meal_prep_style,
            "cooking_time": cooking_time,
            "kitchen_access": kitchen_access,
        }

        with st.spinner("Designing your personalized plan around your constraints, culture, fitness context and budget…"):
            try:
                st.session_state.plan = generate_plan(profile)
                st.session_state.profile_meta = profile
                st.rerun()
            except Exception as exc:
                st.error(f"We couldn't generate your plan right now. {exc}")


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
else:
    plan = st.session_state.plan
    meta = st.session_state.profile_meta or {}

    st.markdown(
        f"""
        <div class="result-hero">
          <div class="result-eyebrow">Your personalized blueprint · {safe(meta.get('country', 'Global'))}</div>
          <div class="result-title">A plan built around your life.</div>
          <div class="result-copy">{safe(plan.get('summary', 'Your plan has been personalized to your selected context.'))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    plan_days = len(plan.get("days", []))
    scope_label = str(meta.get("plan_scope", "Adaptive"))
    metric_values = [
        (str(plan_days), "days planned"),
        (str(meta.get("meals_per_day", "3+")), "meals/day"),
        (safe(meta.get("currency", "")), "planning currency"),
        (safe(meta.get("goal", "Personalized")), "primary goal"),
        ("Strict", "allergy handling"),
    ]

    st.markdown(
        '<div class="metric-grid">' +
        "".join(
            f"<div class='metric-card'><div class='metric-value'>{value}</div><div class='metric-label'>{label}</div></div>"
            for value, label in metric_values
        ) +
        "</div>",
        unsafe_allow_html=True,
    )

    action1, action2, action3 = st.columns(3)
    with action1:
        if st.button("↺ Start a new plan", use_container_width=True):
            st.session_state.plan = None
            st.session_state.profile_meta = None
            st.session_state.saved_plan_id = None
            st.rerun()

    with action2:
        title = f"{meta.get('goal', 'Personalized')} · {meta.get('country', 'Global')} · {datetime.now().strftime('%d %b %Y')}"
        if st.button("♡ Save to history", use_container_width=True):
            saved_id = save_plan_for_user(current_user()["id"], title, plan, meta)
            st.session_state.saved_plan_id = saved_id
            st.success("Saved to your history.")

    with action3:
        docx_bytes = build_docx(plan, meta)
        st.download_button(
            "↓ Download Word plan",
            docx_bytes,
            file_name=f"nourishai-{re.sub(r'[^a-z0-9]+', '-', scope_label.lower()).strip('-') or 'plan'}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )

    with st.expander("Download a plain-text backup", expanded=False):
        st.download_button(
            "Download .txt",
            plan_as_text(plan, meta),
            file_name=f"nourishai-{re.sub(r'[^a-z0-9]+', '-', scope_label.lower()).strip('-') or 'plan'}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    if plan.get("planning_notes"):
        st.markdown(
            f"""
            <div class="soft-note" style="margin-top:.9rem;">
              <b>Planner notes:</b> {safe(plan.get("planning_notes"))}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="section-head">
          <div class="section-kicker">Your plan</div>
          <div class="section-title">Explore your plan, one day at a time.</div>
          <div class="section-sub">Meals include a short rationale, preparation estimate and a safe recipe search link.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for day in plan.get("days", []):
        day_number = int(day.get("day", 1))
        theme = safe(day.get("theme", "Personalized day"))
        budget_fit = safe(day.get("budget_fit", "Personalized").title())
        day_note = safe(day.get("day_note", ""))

        with st.expander(f"DAY {day_number:02d} · {theme}", expanded=(day_number == 1)):
            st.markdown(
                f"""
                <div class="day-card">
                  <div class="day-heading">
                    <div><span class="day-number">{day_number}</span><span class="day-title">{theme}</span></div>
                    <span class="budget-chip">{budget_fit}</span>
                  </div>
                  <div class="day-note">{day_note}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            for meal in day.get("meals", []):
                render_meal(meal, meta.get("country", ""))

    st.markdown(
        f"""
        <div class="safety" style="margin-top:1rem;">
          🛡️ <b>Important:</b> {safe(DISCLAIMER)}
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    f"""
    <div class="footer">
      {APP_NAME} {VERSION} · General wellness & meal-planning support ·
      Built with Streamlit + Groq-compatible AI
    </div>
    """,
    unsafe_allow_html=True,
)
