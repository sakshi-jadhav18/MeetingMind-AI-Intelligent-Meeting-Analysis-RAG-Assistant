import os
import warnings
import logging
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"


import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(
    page_title="MeetMind AI",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --purple:  #7C3AED;
    --purple2: #8B5CF6;
    --purple3: #EDE9FE;
    --pink:    #EC4899;
    --indigo:  #6366F1;
    --green:   #10B981;
    --green2:  #D1FAE5;
    --amber:   #F59E0B;
    --amber2:  #FEF3C7;
    --rose:    #F43F5E;
    --rose2:   #FFE4E6;
    --cyan:    #06B6D4;
    --t1:      #0F172A;
    --t2:      #1E293B;
    --t3:      #475569;
    --t4:      #94A3B8;
    --t5:      #CBD5E1;
    --border:  rgba(148,163,184,0.25);
    --white:   #FFFFFF;
    --bg:      #F8F7FF;
}

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    color: var(--t1) !important;
}

/* FULL PAGE GRADIENT BG */
.stApp {
    background: linear-gradient(160deg,
        #EEE8FF 0%,
        #F5EEFF 20%,
        #FBF0FF 40%,
        #FFF0F8 60%,
        #EEF0FF 80%,
        #E8EEFF 100%
    ) !important;
    min-height: 100vh !important;
}

/* HIDE STREAMLIT CHROME */
#MainMenu, footer, header,
[data-testid="stSidebarCollapsedControl"],
section[data-testid="stSidebar"],
.stDeployButton { display: none !important; }

/* KILL DEFAULT PADDING */
.block-container {
    padding: 0 0 2rem 0 !important;
    max-width: 100% !important;
}
.stApp > div > div > div > div {
    padding: 0 !important;
}
/* Remove Streamlit's injected top gap before first element */
.stApp [data-testid="stAppViewBlockContainer"] > div:first-child {
    padding-top: 0 !important;
    margin-top: 0 !important;
}
/* Remove extra vertical spacing Streamlit adds around markdown blocks */
.stApp [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockSeparator"] {
    display: none !important;
}

/* ════════ TOPNAV ════════ */
/* Compact single-row header rendered as pure HTML */
.mm-topbar {
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2rem;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(148,163,184,0.2);
    width: 100%;
    box-sizing: border-box;
}
/* Suppress Streamlit's own spacing around the markdown block */
[data-testid="stMarkdownContainer"]:has(.mm-topbar) {
    margin: 0 !important;
    padding: 0 !important;
}
.mm-topbar + * { margin-top: 0 !important; }

.mm-nav {
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2rem;
    background: rgba(255,255,255,0.55);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255,255,255,0.7);
    position: sticky;
    top: 0;
    z-index: 200;
}
.mm-logo {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 800;
    font-size: 1.05rem;
    color: var(--t1) !important;
    letter-spacing: -0.02em;
    text-decoration: none;
}
.mm-logo-icon {
    width: 30px; height: 30px;
    border-radius: 8px;
    background: linear-gradient(135deg, var(--purple), var(--pink));
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem;
    line-height: 1;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(124,58,237,0.4);
    font-family: 'Apple Color Emoji', 'Segoe UI Emoji', 'Noto Color Emoji', sans-serif !important;
}
.mm-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--purple);
    background: var(--purple3);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 999px;
    padding: 5px 14px;
}
.mm-badge-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: var(--purple);
    animation: dot-blink 2s infinite;
    flex-shrink: 0;
}
.mm-meta {
    font-size: 0.7rem;
    color: #94A3B8;
    font-weight: 400;
    letter-spacing: 0.01em;
    white-space: nowrap;
}
@keyframes dot-blink { 0%,100%{opacity:0.3} 50%{opacity:1} }

/* ════════ HERO ════════ */
.mm-hero {
    text-align: center;
    padding: 2.2rem 1rem 1.4rem;
}
.mm-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--purple);
    background: var(--purple3);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 999px;
    padding: 5px 14px;
    margin-bottom: 1rem;
}
.mm-h1 {
    font-size: 3.2rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.05em !important;
    line-height: 1.08 !important;
    color: var(--t1) !important;
    margin-bottom: 0.75rem !important;
}
.mm-grad {
    background: linear-gradient(135deg, var(--purple) 0%, var(--pink) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    display: block;
}
.mm-sub {
    font-size: 0.97rem;
    color: #334155;
    line-height: 1.65;
    max-width: 480px;
    margin: 0 auto;
    font-weight: 400;
    text-align: center;
}

/* ════════ INPUT CARD — style the Streamlit column directly ════════ */
div[data-testid="column"].mm-card-col > div[data-testid="stVerticalBlock"] {
    background: rgba(255,255,255,0.82) !important;
    backdrop-filter: blur(40px) !important;
    -webkit-backdrop-filter: blur(40px) !important;
    border: 1px solid rgba(255,255,255,0.95) !important;
    border-radius: 22px !important;
    box-shadow:
        0 16px 48px rgba(124,58,237,0.09),
        0 4px 16px rgba(0,0,0,0.05),
        inset 0 1px 0 rgba(255,255,255,0.85) !important;
    padding: 1.8rem 2rem 1.6rem !important;
}

/* Also target via attribute selector for Streamlit's generated class names */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"]:has(.home-card-anchor) {
    background: rgba(255,255,255,0.82) !important;
    border-radius: 22px !important;
    padding: 1.8rem 2rem !important;
    box-shadow: 0 16px 48px rgba(124,58,237,0.09), 0 4px 16px rgba(0,0,0,0.05) !important;
}

/* SOURCE_INPUT radio label — uppercase, 600, slate */
.stRadio > label {
    text-transform: uppercase !important;
    font-weight: 600 !important;
    color: #475569 !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.08em !important;
}

/* Radio option text (the actual option labels) */
.stRadio [data-testid="stMarkdownContainer"] p,
.stRadio > div > label > div > p {
    color: #000000 !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
}

/* Input/select field labels */
.stTextInput > label,
.stFileUploader > label,
.stSelectbox > label {
    color: #334155 !important;
    font-weight: 500 !important;
    font-size: 0.8rem !important;
}

/* ════════ RESULT CARDS ════════ */
.ri-card {
    background: rgba(255,255,255,0.82);
    border: 1px solid rgba(148,163,184,0.18);
    border-radius: 16px;
    padding: 1.1rem 1.3rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}
.ri-label {
    font-size: 0.67rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.65rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(148,163,184,0.15);
    display: flex;
    align-items: center;
    gap: 5px;
}
.rl-p { color: var(--purple); }
.rl-g { color: var(--green); }
.rl-a { color: var(--amber); }
.rl-r { color: var(--rose); }
.rl-c { color: var(--cyan); }
.ri-body {
    font-size: 0.875rem;
    line-height: 1.82;
    color: var(--t2);
    white-space: pre-line;
}

/* Summary top */
.sum-card {
    background: linear-gradient(135deg, rgba(245,243,255,0.9), rgba(238,242,255,0.9));
    border: 1px solid rgba(124,58,237,0.12);
    border-radius: 16px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 0.8rem;
    position: relative;
    overflow: hidden;
}
.sum-card::before {
    content: '';
    position: absolute; top:0; left:0; right:0;
    height: 3px;
    background: linear-gradient(90deg, var(--purple), var(--pink));
}

/* Transcript */
.tx-card {
    background: rgba(255,255,255,0.8);
    border: 1px solid rgba(148,163,184,0.18);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    font-size: 0.875rem;
    line-height: 1.85;
    color: var(--t2);
    max-height: 68vh;
    overflow-y: auto;
}
.tx-card::-webkit-scrollbar { width: 4px; }
.tx-card::-webkit-scrollbar-thumb { background: var(--t5); border-radius: 2px; }

/* Chat */
.chat-shell {
    background: rgba(255,255,255,0.8);
    border: 1px solid rgba(148,163,184,0.18);
    border-radius: 16px;
    overflow: hidden;
}
.chat-msgs {
    padding: 1.2rem;
    max-height: 52vh;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
}
.chat-msgs::-webkit-scrollbar { width: 4px; }
.chat-msgs::-webkit-scrollbar-thumb { background: var(--t5); border-radius: 2px; }
.crow-ai   { display: flex; gap: 9px; align-items: flex-start; }
.crow-user { display: flex; gap: 9px; align-items: flex-end; justify-content: flex-end; }
.cav-ai {
    width: 30px; height: 30px; border-radius: 50%;
    background: linear-gradient(135deg, var(--purple), var(--indigo));
    display: flex; align-items: center; justify-content: center;
    font-size: 0.62rem; font-weight: 700; color: white; flex-shrink: 0;
}
.cav-user {
    width: 30px; height: 30px; border-radius: 50%;
    background: linear-gradient(135deg, var(--pink), var(--rose));
    display: flex; align-items: center; justify-content: center;
    font-size: 0.58rem; font-weight: 700; color: white; flex-shrink: 0;
}
.cbub-ai {
    background: rgba(245,243,255,0.95);
    border: 1px solid rgba(124,58,237,0.1);
    border-radius: 14px 14px 14px 4px;
    padding: 0.7rem 1rem;
    font-size: 0.86rem; line-height: 1.65; color: var(--t2); max-width: 76%;
}
.cbub-user {
    background: linear-gradient(135deg, var(--purple), var(--indigo));
    border-radius: 14px 14px 4px 14px;
    padding: 0.7rem 1rem;
    font-size: 0.86rem; line-height: 1.65; color: white; max-width: 76%;
}
.chat-input-bar {
    border-top: 1px solid rgba(148,163,184,0.18);
    padding: 0.7rem 1rem;
    background: rgba(248,247,255,0.7);
}

/* Processing steps */
.proc-card {
    background: rgba(255,255,255,0.82);
    backdrop-filter: blur(40px);
    border: 1px solid rgba(255,255,255,0.9);
    border-radius: 24px;
    box-shadow: 0 20px 60px rgba(124,58,237,0.1), 0 4px 20px rgba(0,0,0,0.06);
    padding: 2.5rem;
    width: 100%; max-width: 500px;
    margin: 0 auto;
    text-align: center;
}
.srow {
    display: flex; align-items: center; gap: 10px;
    padding: 7px 12px; border-radius: 10px; margin-bottom: 3px;
    font-size: 0.84rem; text-align: left;
}
.sr-done   { background: var(--green2); }
.sr-active { background: var(--purple3); }
.sr-wait   {}
.si {
    width: 21px; height: 21px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.6rem; font-weight: 700; flex-shrink: 0;
}
.si-done   { background: var(--green); color: white; }
.si-active { background: var(--purple); color: white; animation: sring 1s ease infinite alternate; }
.si-wait   { background: rgba(148,163,184,0.2); color: var(--t4); }
@keyframes sring { from{box-shadow:0 0 0 0 rgba(124,58,237,0.35)} to{box-shadow:0 0 0 6px rgba(124,58,237,0)} }
.st-d { color: var(--green); font-weight: 500; }
.st-a { color: var(--purple); font-weight: 600; }
.st-w { color: var(--t4); }

/* Result header bar */
.res-hbar {
    background: rgba(255,255,255,0.65);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(148,163,184,0.18);
    padding: 0.65rem 1.5rem;
    display: flex; align-items: center; gap: 0.75rem;
}
.res-htitle {
    font-weight: 700; font-size: 0.9rem; color: var(--t1);
    flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.mchip {
    font-size: 0.69rem; font-weight: 500; color: var(--t3);
    background: rgba(255,255,255,0.7); border: 1px solid rgba(148,163,184,0.2);
    border-radius: 6px; padding: 3px 9px;
}

/* Left panel in results */
.lp-mini {
    background: rgba(255,255,255,0.6);
    border: 1px solid rgba(148,163,184,0.15);
    border-radius: 14px;
    padding: 1rem 1.1rem;
    margin-bottom: 0.65rem;
    font-size: 0.8rem; line-height: 1.72; color: var(--t2);
}
.lp-title {
    font-size: 0.67rem; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; color: var(--t3); margin-bottom: 0.5rem;
    display: flex; align-items: center; gap: 5px;
}
.srow2 {
    display: flex; align-items: center; justify-content: space-between;
    padding: 5px 0; border-bottom: 1px solid rgba(148,163,184,0.12);
    font-size: 0.78rem;
}
.srow2:last-child { border-bottom: none; }
.slbl { color: var(--t3); }
.sval { font-weight: 600; color: var(--t1); }

/* ════════ STREAMLIT OVERRIDES ════════ */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea {
    background: rgba(255,255,255,0.85) !important;
    border: 1.5px solid rgba(148,163,184,0.3) !important;
    border-radius: 10px !important;
    color: var(--t1) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 10px 13px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    transition: all 0.18s !important;
}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus {
    border-color: var(--purple) !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.1) !important;
    background: white !important;
}
.stTextInput>div>div>input::placeholder { color: var(--t4) !important; }

.stButton>button {
    background: linear-gradient(135deg, var(--purple) 0%, var(--pink) 100%) !important;
    border: none !important;
    border-radius: 14px !important;
    color: white !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.78rem 1.8rem !important;
    box-shadow: 0 4px 18px rgba(124,58,237,0.32) !important;
    transition: all 0.2s !important;
    letter-spacing: -0.01em !important;
}
.stButton>button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(124,58,237,0.44) !important;
}

/* Ghost button overrides via wrapper */
div[data-testid="mm-ghost"] .stButton>button,
.mm-ghost .stButton>button {
    background: rgba(255,255,255,0.75) !important;
    border: 1.5px solid rgba(148,163,184,0.3) !important;
    color: var(--t2) !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
    font-size: 0.82rem !important;
    padding: 0.5rem 1rem !important;
    border-radius: 10px !important;
}
.mm-ghost .stButton>button:hover {
    border-color: var(--purple) !important;
    color: var(--purple) !important;
    transform: none !important;
}

.stRadio>div { gap: 0.5rem !important; }
.stRadio label { color: var(--t2) !important; font-size: 0.87rem !important; font-weight: 500 !important; }
label { color: var(--t3) !important; font-size: 0.74rem !important; font-weight: 600 !important; }

[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.7) !important;
    border: 1.5px dashed rgba(148,163,184,0.35) !important;
    border-radius: 12px !important;
}

.stSuccess { background: var(--green2) !important; border-color: rgba(16,185,129,0.3) !important; color: var(--green) !important; border-radius: 10px !important; }
.stError   { background: var(--rose2) !important; border-color: rgba(244,63,94,0.3) !important; color: var(--rose) !important; border-radius: 10px !important; }
.stSpinner>div { border-top-color: var(--purple) !important; }
.stInfo    { background: var(--purple3) !important; border-color: rgba(124,58,237,0.2) !important; border-radius: 10px !important; }

.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.55) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 2px !important;
    border: 1px solid rgba(148,163,184,0.2) !important;
    border-bottom: none !important;
    margin-bottom: 0.75rem !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--t3) !important;
    border-radius: 7px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 6px 14px !important;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: var(--purple) !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08) !important;
    font-weight: 600 !important;
}

.stDownloadButton>button {
    background: rgba(255,255,255,0.8) !important;
    border: 1.5px solid rgba(148,163,184,0.25) !important;
    color: var(--t2) !important;
    font-family: 'Inter', sans-serif !important;
    border-radius: 9px !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    padding: 0.45rem 0.85rem !important;
}
.stDownloadButton>button:hover { border-color: var(--purple) !important; color: var(--purple) !important; }

.stFormSubmitButton>button {
    background: var(--purple) !important;
    border: none !important; color: white !important;
    border-radius: 9px !important;
    padding: 0.6rem 1rem !important;
    font-weight: 600 !important; font-size: 0.82rem !important;
    box-shadow: 0 2px 8px rgba(124,58,237,0.25) !important;
}
.stExpander { background: transparent !important; border: 1px solid rgba(148,163,184,0.2) !important; border-radius: 10px !important; }

.stExpander [data-testid="stExpanderDetails"],
.stExpander [data-testid="stExpanderDetails"] * {
    background: transparent !important;
    color: #000000 !important;
}
.stExpander [data-testid="stText"],
.stExpander pre,
.stExpander p,
.stExpander span,
.stExpander div {
    color: #000000 !important;
    background: transparent !important;
}
/* Raw Output tab — fix black text on black bg */
.stExpander [data-testid="stExpanderDetails"] {
    background: rgba(255,255,255,0.95) !important;
    border-radius: 0 0 10px 10px !important;
}
.stExpander [data-testid="stExpanderDetails"] pre,
.stExpander [data-testid="stExpanderDetails"] p,
.stExpander [data-testid="stExpanderDetails"] div,
.stExpander [data-testid="stExpanderDetails"] span {
    color: #1E293B !important;
    background: transparent !important;
}
/* st.text() renders inside a code-like block */
.stExpander .stText,
.stExpander [data-testid="stText"] {
    color: #1E293B !important;
    background: rgba(248,247,255,0.8) !important;
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
    white-space: pre-wrap !important;
    font-size: 0.85rem !important;
    line-height: 1.7 !important;
}




/* Raw Output tab — fix black text on black bg */
.stExpander [data-testid="stExpanderDetails"] {
    background: rgba(255,255,255,0.95) !important;
    border-radius: 0 0 10px 10px !important;
}
.stExpander [data-testid="stExpanderDetails"] pre,
.stExpander [data-testid="stExpanderDetails"] p,
.stExpander [data-testid="stExpanderDetails"] div,
.stExpander [data-testid="stExpanderDetails"] span {
    color: #1E293B !important;
    background: transparent !important;
}
/* st.text() renders inside a code-like block */
.stExpander .stText,
.stExpander [data-testid="stText"] {
    color: #1E293B !important;
    background: rgba(248,247,255,0.8) !important;
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
    white-space: pre-wrap !important;
    font-size: 0.85rem !important;
    line-height: 1.7 !important;
}




/* Raw Output tab — fix black text on black bg */
.stExpander [data-testid="stExpanderDetails"] {
    background: rgba(255,255,255,0.95) !important;
    border-radius: 0 0 10px 10px !important;
}
.stExpander [data-testid="stExpanderDetails"] pre,
.stExpander [data-testid="stExpanderDetails"] p,
.stExpander [data-testid="stExpanderDetails"] div,
.stExpander [data-testid="stExpanderDetails"] span {
    color: #1E293B !important;
    background: transparent !important;
}
/* st.text() renders inside a code-like block */
.stExpander .stText,
.stExpander [data-testid="stText"] {
    color: #1E293B !important;
    background: rgba(248,247,255,0.8) !important;
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
    white-space: pre-wrap !important;
    font-size: 0.85rem !important;
    line-height: 1.7 !important;
}




/* Raw Output tab — fix black text on black bg */
.stExpander [data-testid="stExpanderDetails"] {
    background: rgba(255,255,255,0.95) !important;
    border-radius: 0 0 10px 10px !important;
}
.stExpander [data-testid="stExpanderDetails"] pre,
.stExpander [data-testid="stExpanderDetails"] p,
.stExpander [data-testid="stExpanderDetails"] div,
.stExpander [data-testid="stExpanderDetails"] span {
    color: #1E293B !important;
    background: transparent !important;
}
/* st.text() renders inside a code-like block */
.stExpander .stText,
.stExpander [data-testid="stText"] {
    color: #1E293B !important;
    background: rgba(248,247,255,0.8) !important;
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
    white-space: pre-wrap !important;
    font-size: 0.85rem !important;
    line-height: 1.7 !important;
}




/* Raw Output tab — fix black text on black bg */
.stExpander [data-testid="stExpanderDetails"] {
    background: rgba(255,255,255,0.95) !important;
    border-radius: 0 0 10px 10px !important;
}
.stExpander [data-testid="stExpanderDetails"] pre,
.stExpander [data-testid="stExpanderDetails"] p,
.stExpander [data-testid="stExpanderDetails"] div,
.stExpander [data-testid="stExpanderDetails"] span {
    color: #1E293B !important;
    background: transparent !important;
}
/* st.text() renders inside a code-like block */
.stExpander .stText,
.stExpander [data-testid="stText"] {
    color: #1E293B !important;
    background: rgba(248,247,255,0.8) !important;
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
    white-space: pre-wrap !important;
    font-size: 0.85rem !important;
    line-height: 1.7 !important;
}




/* Raw Output tab — fix black text on black bg */
.stExpander [data-testid="stExpanderDetails"] {
    background: rgba(255,255,255,0.95) !important;
    border-radius: 0 0 10px 10px !important;
}
.stExpander [data-testid="stExpanderDetails"] pre,
.stExpander [data-testid="stExpanderDetails"] p,
.stExpander [data-testid="stExpanderDetails"] div,
.stExpander [data-testid="stExpanderDetails"] span {
    color: #1E293B !important;
    background: transparent !important;
}
/* st.text() renders inside a code-like block */
.stExpander .stText,
.stExpander [data-testid="stText"] {
    color: #1E293B !important;
    background: rgba(248,247,255,0.8) !important;
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
    white-space: pre-wrap !important;
    font-size: 0.85rem !important;
    line-height: 1.7 !important;
}




/* Raw Output tab — fix black text on black bg */
.stExpander [data-testid="stExpanderDetails"] {
    background: rgba(255,255,255,0.95) !important;
    border-radius: 0 0 10px 10px !important;
}
.stExpander [data-testid="stExpanderDetails"] pre,
.stExpander [data-testid="stExpanderDetails"] p,
.stExpander [data-testid="stExpanderDetails"] div,
.stExpander [data-testid="stExpanderDetails"] span {
    color: #1E293B !important;
    background: transparent !important;
}
/* st.text() renders inside a code-like block */
.stExpander .stText,
.stExpander [data-testid="stText"] {
    color: #1E293B !important;
    background: rgba(248,247,255,0.8) !important;
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
    white-space: pre-wrap !important;
    font-size: 0.85rem !important;
    line-height: 1.7 !important;
}




/* Raw Output tab — fix black text on black bg */
.stExpander [data-testid="stExpanderDetails"] {
    background: rgba(255,255,255,0.95) !important;
    border-radius: 0 0 10px 10px !important;
}
.stExpander [data-testid="stExpanderDetails"] pre,
.stExpander [data-testid="stExpanderDetails"] p,
.stExpander [data-testid="stExpanderDetails"] div,
.stExpander [data-testid="stExpanderDetails"] span {
    color: #1E293B !important;
    background: transparent !important;
}
/* st.text() renders inside a code-like block */
.stExpander .stText,
.stExpander [data-testid="stText"] {
    color: #1E293B !important;
    background: rgba(248,247,255,0.8) !important;
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
    white-space: pre-wrap !important;
    font-size: 0.85rem !important;
    line-height: 1.7 !important;
}




/* Raw Output tab — fix black text on black bg */
.stExpander [data-testid="stExpanderDetails"] {
    background: rgba(255,255,255,0.95) !important;
    border-radius: 0 0 10px 10px !important;
}
.stExpander [data-testid="stExpanderDetails"] pre,
.stExpander [data-testid="stExpanderDetails"] p,
.stExpander [data-testid="stExpanderDetails"] div,
.stExpander [data-testid="stExpanderDetails"] span {
    color: #1E293B !important;
    background: transparent !important;
}
/* st.text() renders inside a code-like block */
.stExpander .stText,
.stExpander [data-testid="stText"] {
    color: #1E293B !important;
    background: rgba(248,247,255,0.8) !important;
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
    white-space: pre-wrap !important;
    font-size: 0.85rem !important;
    line-height: 1.7 !important;
}




/* Raw Output tab — fix black text on black bg */
.stExpander [data-testid="stExpanderDetails"] {
    background: rgba(255,255,255,0.95) !important;
    border-radius: 0 0 10px 10px !important;
}
.stExpander [data-testid="stExpanderDetails"] pre,
.stExpander [data-testid="stExpanderDetails"] p,
.stExpander [data-testid="stExpanderDetails"] div,
.stExpander [data-testid="stExpanderDetails"] span {
    color: #1E293B !important;
    background: transparent !important;
}
/* st.text() renders inside a code-like block */
.stExpander .stText,
.stExpander [data-testid="stText"] {
    color: #1E293B !important;
    background: rgba(248,247,255,0.8) !important;
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
    white-space: pre-wrap !important;
    font-size: 0.85rem !important;
    line-height: 1.7 !important;
}




/* Raw Output tab — fix black text on black bg */
.stExpander [data-testid="stExpanderDetails"] {
    background: rgba(255,255,255,0.95) !important;
    border-radius: 0 0 10px 10px !important;
}
.stExpander [data-testid="stExpanderDetails"] pre,
.stExpander [data-testid="stExpanderDetails"] p,
.stExpander [data-testid="stExpanderDetails"] div,
.stExpander [data-testid="stExpanderDetails"] span {
    color: #1E293B !important;
    background: transparent !important;
}
/* st.text() renders inside a code-like block */
.stExpander .stText,
.stExpander [data-testid="stText"] {
    color: #1E293B !important;
    background: rgba(248,247,255,0.8) !important;
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
    white-space: pre-wrap !important;
    font-size: 0.85rem !important;
    line-height: 1.7 !important;
}



hr { border-color: rgba(148,163,184,0.2) !important; margin: 0.6rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────
def init_state():
    for k, v in dict(results=None, chat_history=[], processing=False,
                     error=None, source="", language="english").items():
        if k not in st.session_state:
            st.session_state[k] = v
init_state()

STEPS = [
    "Processing audio source",
    "Transcribing audio",
    "Generating meeting title",
    "Summarizing content",
    "Extracting action items",
    "Extracting key decisions",
    "Extracting open questions",
    "Building RAG knowledge index",
]

# ════════════════════════
# TOPNAV — always shown
# ════════════════════════
if st.session_state.results:
    r = st.session_state.results
    nav1, nav2, nav3 = st.columns([3, 4, 3])
    with nav1:
        st.markdown("""
        <div class="mm-nav" style="position:static;border:none;background:transparent;padding:0.4rem 0">
          <div class="mm-logo">
            <div class="mm-logo-icon" style="line-height:1;font-family:'Apple Color Emoji','Segoe UI Emoji','Noto Color Emoji',sans-serif">&#127897;&#65039;</div>
            MeetMind AI
          </div>
        </div>""", unsafe_allow_html=True)
    with nav2:
        st.markdown(f"""
        <div class="res-hbar" style="border-radius:12px;margin-top:0.3rem">
          <div class="res-htitle">📋 {r['title']}</div>
          <span class="mchip">{len(r['transcript'].split()):,} words</span>
          <span class="mchip">{st.session_state.language.title()}</span>
        </div>""", unsafe_allow_html=True)
    with nav3:
        na, nb, nc = st.columns(3)
        with na:
            st.markdown("<div class='mm-ghost'>", unsafe_allow_html=True)
            if st.button("← New", use_container_width=True, key="new_btn"):
                st.session_state.results = None
                st.session_state.chat_history = []
                st.session_state.error = None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with nb:
            txt = f"MEETMIND AI\n{'='*40}\n\nTITLE\n{r['title']}\n\nSUMMARY\n{r['summary']}\n\nACTION ITEMS\n{r['action_items']}\n\nKEY DECISIONS\n{r['key_decisions']}\n\nOPEN QUESTIONS\n{r['open_questions']}\n\nTRANSCRIPT\n{r['transcript']}"
            st.download_button("⬇ TXT", txt, file_name="meeting.txt", mime="text/plain", use_container_width=True)
        with nc:
            try:
                from fpdf import FPDF
                def gen_pdf(r):
                    pdf = FPDF(); pdf.add_page()
                    pdf.set_font("Helvetica","B",15); pdf.cell(0,10,"MeetMind AI Report",ln=True); pdf.ln(3)
                    for s,c in [("Title",r["title"]),("Summary",r["summary"]),
                                 ("Action Items",r["action_items"]),("Key Decisions",r["key_decisions"]),
                                 ("Open Questions",r["open_questions"])]:
                        pdf.set_font("Helvetica","B",11); pdf.cell(0,8,s,ln=True)
                        pdf.set_font("Helvetica","",10); pdf.multi_cell(0,6,str(c)); pdf.ln(2)
                    return pdf.output(dest="S").encode("latin-1")
                st.download_button("⬇ PDF", gen_pdf(r), file_name="meeting.pdf", mime="application/pdf", use_container_width=True)
            except Exception: pass
else:
    st.markdown("""
    <div class="mm-topbar">
      <div class="mm-logo">
        <div class="mm-logo-icon" style="font-family:'Apple Color Emoji','Segoe UI Emoji','Noto Color Emoji',sans-serif">&#127897;&#65039;</div>
        MeetMind AI
      </div>
      <div class="mm-badge">
        <div class="mm-badge-dot"></div>
        AI Meeting Intelligence
      </div>
      <div class="mm-meta">whisper &middot; mistral &middot; chromadb</div>
    </div>
    """, unsafe_allow_html=True)

# header border is built into mm-topbar / results nav CSS

# Error
if st.session_state.error:
    ec, eb = st.columns([8, 1])
    with ec: st.error(f"⚠ {st.session_state.error}")
    with eb:
        if st.button("✕", key="dis"): st.session_state.error = None; st.rerun()

# ════════════════════════
# HOME SCREEN
# ════════════════════════
if not st.session_state.results and not st.session_state.processing:

    # Hero — pure HTML, centered, no Streamlit column conflicts
    st.markdown("""
    <style>
    .home-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 2rem 1rem 0;
        width: 100%;
    }
    .home-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: #7C3AED;
        background: #EDE9FE;
        border: 1px solid rgba(124,58,237,0.2);
        border-radius: 999px;
        padding: 5px 14px;
        margin-bottom: 1rem;
    }
    .home-h1 {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.05em;
        line-height: 1.08;
        color: #0F172A;
        text-align: center;
        margin: 0 0 0.75rem 0;
    }
    .home-grad {
        background: linear-gradient(135deg, #7C3AED 0%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        display: block;
    }
    .home-sub {
        font-size: 0.97rem;
        color: #334155;
        line-height: 1.65;
        max-width: 480px;
        margin: 0 auto 0 auto;
        font-weight: 400;
        text-align: center;
    }
    /* Glassmorphism card: target the center column's block container */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) > div[data-testid="stVerticalBlock"] {
        background: rgba(255,255,255,0.85) !important;
        backdrop-filter: blur(40px) !important;
        -webkit-backdrop-filter: blur(40px) !important;
        border: 1px solid rgba(255,255,255,0.95) !important;
        border-radius: 22px !important;
        box-shadow: 0 16px 48px rgba(124,58,237,0.09), 0 4px 16px rgba(0,0,0,0.05) !important;
        padding: 1.8rem 2rem 1.6rem !important;
        margin-top: 1.6rem !important;
    }
    </style>
    <div class="home-wrapper">
      <div class="home-eyebrow">&#10022; AI Meeting Intelligence</div>
      <div class="home-h1">Your meetings,<br><span class="home-grad">understood.</span></div>
      <p class="home-sub">Transcribe, summarize, and extract structured insights<br>from any YouTube URL or recording file instantly.</p>
    </div>
    """, unsafe_allow_html=True)

    # Card — center column acts as the card (styled via CSS above)
    _, center, _ = st.columns([1, 5, 1])
    with center:
        # Source selector
        input_mode = st.radio("SOURCE_INPUT",
                               ["▶  YouTube URL", "⬆  Upload File"],
                               horizontal=True, label_visibility="visible")

        # Input field
        if "YouTube" in input_mode:
            source_input = st.text_input("YouTube URL",
                placeholder="Paste YouTube URL here…",
                label_visibility="visible")
        else:
            uploaded = st.file_uploader("Upload audio or video file",
                type=["mp3","mp4","wav","m4a","webm"],
                label_visibility="visible")
            source_input = None
            if uploaded:
                os.makedirs("uploads", exist_ok=True)
                sp = os.path.join("uploads", uploaded.name)
                with open(sp, "wb") as f: f.write(uploaded.read())
                source_input = sp
                st.success(f"✓ Uploaded: {uploaded.name}")

        # Language
        language = st.radio("Transcription Language",
            ["english", "hinglish"],
            horizontal=True,
            format_func=lambda x: " English" if x=="english" else " Hinglish")

        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

        # Analyze button
        go = st.button("✦  Analyze Meeting", use_container_width=True, key="go")

    if go:
        if not source_input:
            st.error("Please provide a YouTube URL or upload a file first.")
        else:
            st.session_state.processing = True
            st.session_state.results = None
            st.session_state.chat_history = []
            st.session_state.error = None
            st.session_state.source = source_input
            st.session_state.language = language
            st.rerun()

# ════════════════════════
# PROCESSING SCREEN
# ════════════════════════
elif st.session_state.processing:
    st.markdown("<div style='padding:3rem 1rem'>", unsafe_allow_html=True)
    _, cc, _ = st.columns([1, 4, 1])
    with cc:
        ph = st.empty()

        def render(cur):
            rows = ""
            for i, s in enumerate(STEPS):
                if i < cur:
                    rows += f"<div class='srow sr-done'><div class='si si-done'>✓</div><span class='st-d'>{s}</span></div>"
                elif i == cur:
                    rows += f"<div class='srow sr-active'><div class='si si-active'>◎</div><span class='st-a'>{s}…</span></div>"
                else:
                    rows += f"<div class='srow sr-wait'><div class='si si-wait'>{i+1}</div><span class='st-w'>{s}</span></div>"
            ph.markdown(f"""
            <div class='proc-card'>
              <div style='font-size:2rem;margin-bottom:0.8rem'>⚡</div>
              <div style='font-size:1.25rem;font-weight:700;color:var(--t1);letter-spacing:-0.025em;margin-bottom:0.25rem'>
                Analyzing your meeting
              </div>
              <p style='font-size:0.84rem;color:var(--t3);margin-bottom:1.4rem'>
                This usually takes 1–3 minutes.
              </p>
              {rows}
            </div>""", unsafe_allow_html=True)

        try:
            from utils.audio_processor import process_input
            from core.transcriber import transcribe_all
            from core.sammarize import summarize, generate_title
            from core.extractor import extract_action_items, extract_key_decisions, extract_questions
            from core.rag_engine import build_rag_chain

            src = st.session_state.source
            lang = st.session_state.language

            render(0); chunks = process_input(src, language=lang)
            render(1); transcript = transcribe_all(chunks, language=lang)
            render(2); title = generate_title(transcript)
            render(3); summary = summarize(transcript)
            render(4); action_items = extract_action_items(transcript)
            render(5); decisions = extract_key_decisions(transcript)
            render(6); questions = extract_questions(transcript)

            render(3)
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=4) as executor:
                f_sum  = executor.submit(summarize, transcript)
                f_act  = executor.submit(extract_action_items, transcript)
                f_dec  = executor.submit(extract_key_decisions, transcript)
                f_que  = executor.submit(extract_questions, transcript) 
                summary      = f_sum.result()
                action_items = f_act.result()   
                decisions    = f_dec.result()
                questions    = f_que.result()
            render(4);
            render(5);
            render(6)
            render(7); rag_chain = build_rag_chain(transcript)
            render(len(STEPS))

            st.session_state.results = dict(
                title=title, transcript=transcript, summary=summary,
                action_items=action_items, key_decisions=decisions,
                open_questions=questions, rag_chain=rag_chain)
        except Exception as e:
            st.session_state.error = str(e); ph.empty()

        st.session_state.processing = False
    st.markdown("</div>", unsafe_allow_html=True)
    st.rerun()

# ════════════════════════
# RESULTS SCREEN
# ════════════════════════
elif st.session_state.results:
    r = st.session_state.results
    words = len(r["transcript"].split())

    left_col, right_col = st.columns([22, 78], gap="small")

    # ── LEFT PANEL ──
    with left_col:
        st.markdown(f"""
        <div style='padding:0.8rem 0.4rem'>
          <div class='lp-mini'>
            <div class='lp-title'>📋 Meeting Summary</div>
            <div style='font-size:0.79rem;line-height:1.7;color:var(--t2)'>
              {r['summary'][:280]}{'…' if len(r['summary'])>280 else ''}
            </div>
          </div>
          <div class='lp-mini'>
            <div class='lp-title'>📊 Quick Stats</div>
            <div class='srow2'><span class='slbl'>📝 Words</span><span class='sval'>{words:,}</span></div>
            <div class='srow2'><span class='slbl'>🌐 Language</span><span class='sval'>{st.session_state.language.title()}</span></div>
          </div>
        </div>""", unsafe_allow_html=True)

    # ── RIGHT PANEL ──
    with right_col:
        tab1, tab2, tab3, tab4 = st.tabs([
            "  Summary & Insights  ",
            "  Transcript  ",
            "  Chat with Meeting  ",
            "  Raw Output  "
        ])

        with tab1:
            st.markdown(f"""
            <div class='sum-card'>
              <div class='ri-label rl-p'>Executive Summary</div>
              <div class='ri-body'>{r['summary']}</div>
            </div>""", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3, gap="small")
            with c1:
                st.markdown(f"""
                <div class='ri-card'>
                  <div class='ri-label rl-g'>✅ Action Items</div>
                  <div class='ri-body'>{r['action_items']}</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class='ri-card'>
                  <div class='ri-label rl-a'>🔑 Key Decisions</div>
                  <div class='ri-body'>{r['key_decisions']}</div>
                </div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class='ri-card'>
                  <div class='ri-label rl-r'>❓ Open Questions</div>
                  <div class='ri-body'>{r['open_questions']}</div>
                </div>""", unsafe_allow_html=True)

        with tab2:
            st.markdown(f"<div class='tx-card'>{r['transcript']}</div>", unsafe_allow_html=True)

        with tab3:
            # Chat shell
            st.markdown("""
            <div class='chat-shell'>
              <div class='chat-msgs'>
            """, unsafe_allow_html=True)

            # Welcome or history
            if not st.session_state.chat_history:
                st.markdown("""
                <div class='crow-ai'>
                  <div class='cav-ai'>AI</div>
                  <div class='cbub-ai'>Hi! I'm your AI meeting assistant. Ask me anything about this meeting — decisions, action items, key topics, or any specific details.</div>
                </div>""", unsafe_allow_html=True)
            else:
                for msg in st.session_state.chat_history:
                    if msg["role"] == "user":
                        st.markdown(f"""
                        <div class='crow-user'>
                          <div class='cbub-user'>{msg['content']}</div>
                          <div class='cav-user'>You</div>
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class='crow-ai'>
                          <div class='cav-ai'>AI</div>
                          <div class='cbub-ai'>{msg['content']}</div>
                        </div>""", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)  # chat-msgs

            # Input bar inside shell
            st.markdown("<div class='chat-input-bar'>", unsafe_allow_html=True)
            with st.form("chat_form", clear_on_submit=True):
                fi, fb = st.columns([6, 1])
                with fi:
                    user_q = st.text_input("q", placeholder="Ask anything about this meeting…",
                                           label_visibility="collapsed")
                with fb:
                    send = st.form_submit_button("Send", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)  # chat-shell

            if send and user_q.strip():
                from core.rag_engine import ask_question
                st.session_state.chat_history.append({"role":"user","content":user_q})
                with st.spinner(""):
                    answer = ask_question(r["rag_chain"], user_q)
                st.session_state.chat_history.append({"role":"assistant","content":answer})
                st.rerun()

            if st.session_state.chat_history:
                st.markdown("<div class='mm-ghost'>", unsafe_allow_html=True)
                if st.button("✕ Clear Chat", key="clr"):
                    st.session_state.chat_history = []
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        with tab4:
            for lbl, key in [("Title","title"),("Summary","summary"),
                              ("Action Items","action_items"),
                              ("Key Decisions","key_decisions"),
                              ("Open Questions","open_questions")]:
                with st.expander(lbl):
                    st.text(r[key])