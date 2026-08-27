import streamlit as st
import pandas as pd

from agents.signal_agent import detect_signal
from agents.diagnostic_agent import diagnose_revenue_change
from agents.strategist_agent import generate_strategy

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="KPI Storytelling Engine",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# DESIGN TOKENS & STYLES
# ============================================================

CASE_ID = "KPI-2026-08"

st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">

<style>

    :root {
        --ink: #10162a;
        --ink-2: #0d1222;
        --panel: #161d35;
        --panel-2: #1b2440;
        --panel-3: #1f2847;
        --line: #2a3358;
        --line-2: #3a4568;
        --paper: #e7dcc0;
        --paper-2: #d4c9b0;
        --brick: #b0473a;
        --brick-2: #c95647;
        --sage: #6a8f5c;
        --sage-2: #7aa36a;
        --muted: #8a94b3;
        --text: #eef0f6;
        --glow-brick: rgba(176, 71, 58, 0.15);
        --glow-sage: rgba(106, 143, 92, 0.12);
    }

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(1200px 500px at 15% -5%, rgba(176,71,58,0.07), transparent 60%),
            radial-gradient(900px 500px at 100% 0%, rgba(106,143,92,0.05), transparent 55%),
            linear-gradient(rgba(255, 255, 255, 0.015) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.015) 1px, transparent 1px),
            var(--ink);
        background-size: 
            100% 100%,
            100% 100%,
            40px 40px,
            40px 40px,
            100% 100%;
        color: var(--text);
    }

    .block-container {
        max-width: 1320px;
        padding-top: 1.6rem;
        padding-bottom: 4rem;
    }

    /* ---------------- Header / case file tab ---------------- */

    .case-tab {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: linear-gradient(180deg, var(--paper), var(--paper-2));
        color: #2a2213;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 1.5px;
        padding: 8px 16px 8px 16px;
        border-radius: 0 0 10px 10px;
        margin-bottom: 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
        position: relative;
    }

    .case-tab::after {
        content: "";
        position: absolute;
        bottom: -1px;
        left: 12px;
        right: 12px;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(42, 34, 19, 0.3), transparent);
    }

    .hero {
        border: 1px solid var(--line);
        border-top: none;
        border-radius: 0 12px 12px 12px;
        background: linear-gradient(180deg, var(--panel-2), var(--panel));
        padding: 32px 36px 30px 36px;
        margin-bottom: 40px;
        position: relative;
        overflow: hidden;
    }

    .hero::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, var(--line), var(--panel-3), var(--line));
    }

    .hero-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 32px;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 6px;
        color: var(--text);
    }

    .hero-subtitle {
        color: var(--muted);
        font-size: 15px;
        font-family: 'Source Serif 4', serif;
        font-style: italic;
    }

    /* ---------------- Section headings ---------------- */

    .section-eyebrow {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 2px;
        color: var(--paper);
        text-transform: uppercase;
        margin-top: 36px;
        margin-bottom: 2px;
    }

    .section-title {
        font-size: 20px;
        font-weight: 650;
        margin-top: 2px;
        margin-bottom: 4px;
        color: var(--text);
    }

    .section-caption {
        color: var(--muted);
        font-size: 13px;
        margin-bottom: 16px;
        border-bottom: 1px dashed var(--line);
        padding-bottom: 14px;
    }

    /* ---------------- Evidence / KPI cards ---------------- */

    .card {
        position: relative;
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 4px 10px 10px 10px;
        padding: 18px 20px;
        height: 100%;
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
    }

    .card:hover {
        transform: translateY(-2px);
        border-color: var(--line-2);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
    }

    .card::before {
        content: "";
        position: absolute;
        top: 0; left: 0;
        width: 26px; height: 26px;
        background: linear-gradient(135deg, transparent 50%, var(--ink) 50%);
        border-radius: 4px 0 0 0;
        transition: background 0.18s ease;
    }

    .card:hover::before {
        background: linear-gradient(135deg, transparent 50%, var(--panel-3) 50%);
    }

    .card-label {
        color: var(--muted);
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1.2px;
        margin-bottom: 10px;
    }

    .card-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 26px;
        font-weight: 700;
        color: var(--text);
    }

    .card-sub {
        color: var(--muted);
        font-size: 12px;
        margin-top: 6px;
    }

    /* ---------------- Case summary (story) ---------------- */

    .story {
        background: linear-gradient(180deg, var(--panel), var(--panel-2));
        border: 1px solid var(--line);
        border-left: 4px solid var(--brick);
        border-radius: 4px 10px 10px 4px;
        padding: 28px 32px;
        margin-top: 8px;
        margin-bottom: 8px;
        position: relative;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
    }

    .story::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: 
            repeating-linear-gradient(
                0deg,
                transparent,
                transparent 2px,
                rgba(0, 0, 0, 0.02) 2px,
                rgba(0, 0, 0, 0.02) 4px
            );
        pointer-events: none;
        border-radius: 4px 10px 10px 4px;
    }

    .story-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.6px;
        color: var(--muted);
        text-transform: uppercase;
        margin-bottom: 12px;
        position: relative;
        z-index: 1;
    }

    .story-text {
        font-family: 'Source Serif 4', serif;
        font-size: 19px;
        line-height: 1.62;
        font-weight: 400;
        color: var(--text);
        position: relative;
        z-index: 1;
    }

    .story-text b {
        color: var(--paper);
        font-weight: 600;
    }

    /* ---------------- Stamp (signature element) ---------------- */

    .stamp {
        display: inline-block;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 700;
        font-size: 13px;
        letter-spacing: 2px;
        text-transform: uppercase;
        padding: 8px 18px;
        border: 2px dashed;
        border-radius: 6px;
        transform: rotate(-2deg);
        margin-top: 6px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        z-index: 1;
    }

    .stamp:hover {
        transform: rotate(0deg) scale(1.02);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    .stamp-alert {
        color: var(--brick);
        border-color: var(--brick);
        background: rgba(176, 71, 58, 0.1);
        box-shadow: 0 0 20px var(--glow-brick);
    }

    .stamp-normal {
        color: var(--sage);
        border-color: var(--sage);
        background: rgba(106, 143, 92, 0.1);
        box-shadow: 0 0 20px var(--glow-sage);
    }

    /* ---------------- Agent / exhibit cards ---------------- */

    .agent {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 20px 22px;
        min-height: 180px;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .agent:hover {
        border-color: var(--paper);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    }

    .exhibit-tag {
        display: inline-block;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10.5px;
        font-weight: 700;
        letter-spacing: 1px;
        color: #2a2213;
        background: var(--paper);
        padding: 3px 9px;
        border-radius: 4px;
        margin-bottom: 12px;
    }

    .agent-name {
        font-size: 16px;
        font-weight: 650;
        margin-bottom: 12px;
        color: var(--text);
    }

    .agent-text {
        color: #c5cce0;
        line-height: 1.6;
        font-size: 13.5px;
    }

    .agent-text b {
        color: var(--text);
    }

    /* ---------------- Recommendation ---------------- */

    .recommendation {
        background: var(--panel);
        border: 1px solid var(--line);
        border-top: 3px solid var(--sage);
        border-radius: 4px 10px 10px 10px;
        padding: 26px 28px;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .recommendation:hover {
        border-color: var(--line-2);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    }

    .recommendation-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--sage);
        margin-bottom: 10px;
    }

    .recommendation-text {
        font-family: 'Source Serif 4', serif;
        font-size: 17px;
        line-height: 1.6;
        color: var(--text);
    }

    .recommendation .meta-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        letter-spacing: 1px;
        color: var(--muted);
        text-transform: uppercase;
    }

    /* ---------------- Human sign-off ---------------- */

    .human {
        background: var(--panel-2);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 16px 20px;
        margin-top: 18px;
        display: flex;
        gap: 14px;
        align-items: flex-start;
        transition: border-color 0.2s ease;
    }

    .human:hover {
        border-color: var(--line-2);
    }

    .human-title {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 700;
        font-size: 12px;
        letter-spacing: 1px;
        color: var(--paper);
        text-transform: uppercase;
        white-space: nowrap;
    }

    .human-text {
        color: var(--muted);
        font-size: 13px;
        line-height: 1.5;
    }

    /* ---------------- Misc ---------------- */

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 10px;
        overflow: hidden;
        background: var(--panel);
    }

    [data-testid="stDataFrame"] th {
        background: var(--panel-2);
        color: var(--paper);
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        border-bottom: 2px solid var(--line);
        padding: 12px 16px;
    }

    [data-testid="stDataFrame"] td {
        background: var(--panel);
        color: var(--text);
        font-size: 13px;
        border-bottom: 1px solid var(--line);
        padding: 12px 16px;
        transition: background 0.15s ease;
    }

    [data-testid="stDataFrame"] tr:hover td {
        background: var(--panel-2);
    }

    [data-testid="stDataFrame"] tr:nth-child(even) td {
        background: rgba(255, 255, 255, 0.02);
    }

    [data-testid="stDataFrame"] tr:nth-child(even):hover td {
        background: var(--panel-2);
    }

    /* ---------------- Focus states ---------------- */

    input:focus,
    button:focus,
    [data-testid="stVerticalBlock"]:focus-within {
        outline: 2px solid var(--paper);
        outline-offset: 2px;
    }

    .card:focus-within,
    .agent:focus-within {
        border-color: var(--paper);
        box-shadow: 0 0 0 2px var(--glow-sage);
    }

    /* ---------------- Responsive ---------------- */

    @media (max-width: 1100px) {
        .block-container {
            max-width: 100%;
            padding-left: 2rem;
            padding-right: 2rem;
        }
    }

    @media (max-width: 768px) {
        .hero {
            padding: 24px 20px 22px 20px;
        }
        
        .hero-title {
            font-size: 26px;
        }
        
        .card-value {
            font-size: 22px;
        }
        
        .story-text {
            font-size: 16px;
        }
        
        .agent {
            min-height: auto;
        }
    }

</style>
""", unsafe_allow_html=True)

# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    orders = pd.read_csv("data/olist_orders_dataset.csv")
    items = pd.read_csv("data/olist_order_items_dataset.csv")
    products = pd.read_csv("data/olist_products_dataset.csv")
    reviews = pd.read_csv("data/olist_order_reviews_dataset.csv")
    return orders, items, products, reviews

orders, items, products, reviews = load_data()

# ============================================================
# MONTHLY REVENUE
# ============================================================

order_revenue = items.groupby("order_id")["price"].sum().reset_index()
data = orders.merge(order_revenue, on="order_id")
data["order_purchase_timestamp"] = pd.to_datetime(data["order_purchase_timestamp"])
data["month"] = data["order_purchase_timestamp"].dt.to_period("M")
monthly_revenue = data.groupby("month")["price"].sum().reset_index()

# ============================================================
# SIGNAL AGENT
# ============================================================

signal = detect_signal(monthly_revenue)

# ============================================================
# DIAGNOSTIC AGENT
# ============================================================

diagnosis, latest_month, previous_month, themes = diagnose_revenue_change(
    orders, items, products, reviews
)

# ============================================================
# STRATEGIST AGENT
# ============================================================

strategy = generate_strategy(signal, diagnosis, themes, latest_month, previous_month)

# ============================================================
# GET REVENUE VALUES
# ============================================================

latest_revenue = monthly_revenue[monthly_revenue["month"] == signal["latest_month"]]["price"].iloc[0]
previous_revenue = monthly_revenue[monthly_revenue["month"] == previous_month]["price"].iloc[0]
is_alert = str(signal["signal"]).strip().lower() not in ("normal", "normal variance", "no anomaly")

# ============================================================
# HEADER
# ============================================================

st.markdown(f"""
<div class="case-tab">📁 CASE FILE No. {CASE_ID}</div>

<div class="hero">
    <div class="hero-title">KPI Storytelling Engine</div>
    <div class="hero-subtitle">
        Three agents build the case on a revenue movement — evidence first, verdict last, decision always human.
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# TOP KPI CARDS
# ============================================================

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="card">
        <div class="card-label">LATEST REVENUE</div>
        <div class="card-value">₹{latest_revenue:,.0f}</div>
        <div class="card-sub">{latest_month}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
        <div class="card-label">MONTH-OVER-MONTH</div>
        <div class="card-value">{signal["latest_change"]:.2f}%</div>
        <div class="card-sub">{previous_month} → {latest_month}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="card">
        <div class="card-label">SIGNAL</div>
        <div class="card-value">{signal["signal"]}</div>
        <div class="card-sub">Z-score: {signal["z_score"]:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="card">
        <div class="card-label">ANALYSIS WINDOW</div>
        <div class="card-value">{previous_month}</div>
        <div class="card-sub">compared with {latest_month}</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# CASE SUMMARY (executive story)
# ============================================================

st.markdown(
    '<div class="section-eyebrow">Case Summary</div>'
    '<div class="section-title">📖 What changed, why, and what to do next</div>',
    unsafe_allow_html=True
)

top_category = diagnosis[diagnosis["revenue_change"] < 0].iloc[0]["product_category_name"]
top_category_change = diagnosis[diagnosis["revenue_change"] < 0].iloc[0]["percentage_change"]
top_theme = max(themes, key=themes.get)

story = (
    f"Revenue changed by <b>{signal['latest_change']:.2f}%</b> "
    f"in {latest_month}, but the Signal Agent classifies this "
    f"movement as <b>{signal['signal'].lower()}</b>. "
    f"The largest category-level decline came from "
    f"<b>{top_category}</b>, down {top_category_change:.1f}%. "
    f"Customer reviews are most strongly associated with "
    f"<b>{top_theme.lower()}</b> issues."
)

stamp_class = "stamp-alert" if is_alert else "stamp-normal"
stamp_text = signal["signal"]

st.markdown(
    f"""
    <div class="story">
        <div class="story-label">Filed evidence — Read before acting</div>
        <div class="story-text">{story}</div>
        <br>
        <span class="stamp {stamp_class}">Verdict: {stamp_text}</span>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# REVENUE TREND
# ============================================================

st.markdown(
    '<div class="section-eyebrow">Exhibit A</div>'
    '<div class="section-title">📈 Revenue Trend</div>'
    '<div class="section-caption">Completed months only — incomplete periods are excluded from the signal.</div>',
    unsafe_allow_html=True
)

chart_data = monthly_revenue[monthly_revenue["month"] <= signal["latest_month"]].copy()
chart_data["month"] = chart_data["month"].astype(str)
chart_data = chart_data.rename(columns={"price": "Revenue (₹)"})
chart_data = chart_data.set_index("month")

latest_month_str = str(signal["latest_month"])

st.markdown(f"""
<div style="
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
">
    <div style="
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: {'var(--brick)' if is_alert else 'var(--sage)'};
        box-shadow: 0 0 12px {'var(--glow-brick)' if is_alert else 'var(--glow-sage)'};
    "></div>
    <div style="
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        color: var(--muted);
    ">
        Latest period: <b style="color: var(--text)">{latest_month_str}</b> • 
        Change: <b style="color: {'var(--brick)' if is_alert else 'var(--sage)'}">{signal['latest_change']:.2f}%</b>
    </div>
</div>
""", unsafe_allow_html=True)

st.line_chart(
    chart_data["Revenue (₹)"],
    height=320,
    color="#b0473a" if is_alert else "#6a8f5c"
)

# ============================================================
# TWO-COLUMN AGENT VIEW
# ============================================================

left, right = st.columns(2)

with left:
    st.markdown(
        '<div class="section-eyebrow">Exhibit B</div>'
        '<div class="section-title">🔎 Signal Agent</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f"""
        <div class="agent">
            <div class="exhibit-tag">STATISTICAL TEST</div>
            <div class="agent-name">Is the change actually unusual?</div>
            <div class="agent-text">
                <b>Revenue change:</b> {signal["latest_change"]:.2f}%<br><br>
                <b>Historical average:</b> {signal["historical_mean"]:.2f}%<br><br>
                <b>Historical standard deviation:</b> {signal["historical_std"]:.2f}<br><br>
                <b>Z-score:</b> {signal["z_score"]:.2f}<br><br>
                <b>Conclusion:</b> {signal["signal"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with right:
    st.markdown(
        '<div class="section-eyebrow">Exhibit C</div>'
        '<div class="section-title">💬 Customer Voice</div>',
        unsafe_allow_html=True
    )
    theme_df = pd.DataFrame(
        list(themes.items()),
        columns=["Theme", "Negative Reviews"]
    ).sort_values("Negative Reviews", ascending=True)
    st.bar_chart(
        theme_df.set_index("Theme"),
        height=250,
        color="#b0473a",
        horizontal=True
    )

# ============================================================
# DIAGNOSTIC AGENT
# ============================================================

st.markdown(
    '<div class="section-eyebrow">Exhibit D</div>'
    '<div class="section-title">🧠 Diagnostic Agent</div>'
    f'<div class="section-caption">Evidence behind the {previous_month} → {latest_month} movement</div>',
    unsafe_allow_html=True
)

display_data = diagnosis[
    ["product_category_name", "latest_revenue", "previous_revenue", "revenue_change", "percentage_change"]
].head(8).copy()

display_data.columns = ["Category", "Latest Revenue", "Previous Revenue", "Revenue Change", "% Change"]

def _color_change(val):
    color = "#e08a7d" if val < 0 else "#9dc191"
    return f"color: {color}; font-weight: 600;"

styled_table = (
    display_data.style
    .format({
        "Latest Revenue": "₹{:,.0f}",
        "Previous Revenue": "₹{:,.0f}",
        "Revenue Change": "₹{:,.0f}",
        "% Change": "{:.1f}%",
    })
    .map(_color_change, subset=["Revenue Change", "% Change"])
)

st.dataframe(
    styled_table,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# STRATEGIST
# ============================================================

st.markdown(
    '<div class="section-eyebrow">Exhibit E</div>'
    '<div class="section-title">🎯 Strategist Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="recommendation">
        <div class="recommendation-title">Recommended Next Step</div>
        <div class="recommendation-text">{strategy["recommendation"]}</div>
        <br>
        <span class="meta-label">Why</span><br>
        {strategy["reason"]}
        <br><br>
        <span class="meta-label">Confidence</span><br>
        {strategy["confidence"]}
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# HUMAN IN THE LOOP
# ============================================================

st.markdown(
    """
    <div class="human">
        <div class="human-title">✍️ Sign-off</div>
        <div class="human-text">
            The engine files evidence and a recommendation. It does not close the case —
            that decision, and the accountability for it, stays with a human.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    f"""
    <br><br>
    <div style="
        text-align:center;
        color:#5b6584;
        font-family: 'IBM Plex Mono', monospace;
        font-size:11px;
        letter-spacing: 1px;
    ">
        KPI STORYTELLING ENGINE · CASE {CASE_ID} · EVIDENCE BEFORE ACTION
    </div>
    """,
    unsafe_allow_html=True
)