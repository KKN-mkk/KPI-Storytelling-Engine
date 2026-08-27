import time
import streamlit as st
import pandas as pd
from datetime import datetime

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

CASE_ID = "KPI-2026-08"


# ============================================================
# DESIGN TOKENS
# ============================================================

st.markdown(
    """
<style>

:root {
    --ink: #10162a;
    --panel: #161d35;
    --panel-2: #1b2440;
    --line: #2a3358;
    --paper: #e7dcc0;
    --brick: #b0473a;
    --sage: #6a8f5c;
    --muted: #8a94b3;
    --text: #eef0f6;
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            1200px 500px at 15% -5%,
            rgba(176,71,58,0.07),
            transparent 60%
        ),
        radial-gradient(
            900px 500px at 100% 0%,
            rgba(106,143,92,0.05),
            transparent 55%
        ),
        linear-gradient(
            rgba(255,255,255,0.015) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(255,255,255,0.015) 1px,
            transparent 1px
        ),
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


/* ============================================================
   HEADER
   ============================================================ */

.case-tab {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(
        180deg,
        var(--paper),
        #d4c9b0
    );
    color: #2a2213;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1.5px;
    padding: 8px 16px;
    border-radius: 0 0 10px 10px;
}

.hero {
    border: 1px solid var(--line);
    border-top: none;
    border-radius: 0 12px 12px 12px;
    background: linear-gradient(
        180deg,
        var(--panel-2),
        var(--panel)
    );
    padding: 32px 36px;
    margin-bottom: 40px;
}

.hero-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 32px;
    font-weight: 700;
    color: var(--text);
}

.hero-subtitle {
    color: var(--muted);
    font-size: 15px;
    font-family: 'Source Serif 4', serif;
    font-style: italic;
}


/* ============================================================
   SECTIONS
   ============================================================ */

.section-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    color: var(--paper);
    text-transform: uppercase;
    margin-top: 36px;
}

.section-title {
    font-size: 20px;
    font-weight: 650;
    color: var(--text);
}

.section-caption {
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 16px;
    border-bottom: 1px dashed var(--line);
    padding-bottom: 14px;
}


/* ============================================================
   CARDS
   ============================================================ */

.card {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 4px 10px 10px 10px;
    padding: 18px 20px;
    min-height: 110px;
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


/* ============================================================
   STORY
   ============================================================ */

.story {
    background: linear-gradient(
        180deg,
        var(--panel),
        var(--panel-2)
    );
    border: 1px solid var(--line);
    border-left: 4px solid var(--brick);
    border-radius: 4px 10px 10px 4px;
    padding: 28px 32px;
}

.story-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.6px;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 12px;
}

.story-text {
    font-family: 'Source Serif 4', serif;
    font-size: 19px;
    line-height: 1.62;
    color: var(--text);
}

.story-text b {
    color: var(--paper);
}


/* ============================================================
   AGENTS
   ============================================================ */

.agent {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 20px 22px;
    min-height: 180px;
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


/* ============================================================
   RECOMMENDATION
   ============================================================ */

.recommendation {
    background: var(--panel);
    border: 1px solid var(--line);
    border-top: 3px solid var(--sage);
    border-radius: 4px 10px 10px 10px;
    padding: 26px 28px;
}

.recommendation-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--sage);
}

.recommendation-text {
    font-family: 'Source Serif 4', serif;
    font-size: 17px;
    line-height: 1.6;
    color: var(--text);
}

.meta-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 1px;
    color: var(--muted);
    text-transform: uppercase;
}


/* ============================================================
   INVESTIGATION
   ============================================================ */

.investigation {
    background: linear-gradient(
        180deg,
        var(--panel-2),
        var(--panel)
    );
    border: 1px solid var(--line);
    border-left: 4px solid var(--paper);
    border-radius: 4px 10px 10px 4px;
    padding: 26px 28px;
}

.investigation-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1.4px;
    color: var(--paper);
    text-transform: uppercase;
}

.investigation-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 24px;
    font-weight: 700;
    color: var(--text);
}

.evidence-box {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 18px;
    height: 100%;
}

.evidence-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 1.2px;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 8px;
}

.evidence-text {
    font-size: 13px;
    color: var(--text);
    line-height: 1.55;
}


/* ============================================================
   HUMAN SIGN-OFF
   ============================================================ */

.human {
    background: var(--panel-2);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 16px 20px;
    margin-top: 18px;
}

.human-title {
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 1px;
    color: var(--paper);
    text-transform: uppercase;
}

.human-text {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.5;
    margin-top: 8px;
}

</style>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link
href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=IBM+Plex+Sans:wght@400;500;600&display=swap"
rel="stylesheet">
""",
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    orders = pd.read_csv(
        "data/olist_orders_dataset.csv"
    )

    items = pd.read_csv(
        "data/olist_order_items_dataset.csv"
    )

    products = pd.read_csv(
        "data/olist_products_dataset.csv"
    )

    reviews = pd.read_csv(
        "data/olist_order_reviews_dataset.csv"
    )

    return (
        orders,
        items,
        products,
        reviews
    )


orders, items, products, reviews = load_data()


# ============================================================
# PREPARE BASE DATA
# ============================================================

orders = orders.copy()
items = items.copy()
products = products.copy()
reviews = reviews.copy()

orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"],
    errors="coerce"
)

orders = orders.dropna(
    subset=["order_purchase_timestamp"]
).copy()

orders["month"] = (
    orders["order_purchase_timestamp"]
    .dt.to_period("M")
)

items["price"] = pd.to_numeric(
    items["price"],
    errors="coerce"
).fillna(0)


# ============================================================
# REVENUE
# ============================================================

order_revenue = (
    items.groupby("order_id")["price"]
    .sum()
    .reset_index()
)

data = orders.merge(
    order_revenue,
    on="order_id",
    how="inner"
)

monthly_revenue = (
    data.groupby("month")["price"]
    .sum()
    .reset_index()
)


# ============================================================
# OTHER KPIs
# ============================================================

monthly_orders = (
    orders.groupby("month")
    .size()
    .reset_index(name="orders")
)

monthly_aov = monthly_revenue.merge(
    monthly_orders,
    on="month",
    how="left"
)

monthly_aov["aov"] = (
    monthly_aov["price"]
    / monthly_aov["orders"].replace(
        0,
        pd.NA
    )
)


# ============================================================
# CUSTOMER RATING
# ============================================================

review_kpi = reviews.merge(
    orders[
        [
            "order_id",
            "month"
        ]
    ],
    on="order_id",
    how="inner"
)

review_kpi["review_score"] = pd.to_numeric(
    review_kpi["review_score"],
    errors="coerce"
)

monthly_rating = (
    review_kpi.groupby("month")[
        "review_score"
    ]
    .mean()
    .reset_index(name="avg_rating")
)


# ============================================================
# AGENT PIPELINE
# ============================================================

pipeline_start = time.perf_counter()

signal = detect_signal(
    monthly_revenue
)

(
    diagnosis,
    latest_month,
    previous_month,
    themes
) = diagnose_revenue_change(
    orders,
    items,
    products,
    reviews
)

strategy = generate_strategy(
    signal,
    diagnosis,
    themes,
    latest_month,
    previous_month
)

pipeline_latency = (
    time.perf_counter()
    - pipeline_start
)


# ============================================================
# IMPORTANT:
# Align ALL UI with Signal Agent's latest COMPLETE month
# ============================================================

latest_signal_month = pd.Period(
    signal["latest_month"],
    freq="M"
)

previous_signal_month = (
    latest_signal_month - 1
)


# ============================================================
# LATEST REVENUE
# ============================================================

latest_revenue_row = monthly_revenue[
    monthly_revenue["month"]
    == latest_signal_month
]

previous_revenue_row = monthly_revenue[
    monthly_revenue["month"]
    == previous_signal_month
]

latest_revenue = (
    latest_revenue_row["price"].iloc[0]
    if not latest_revenue_row.empty
    else 0
)

previous_revenue = (
    previous_revenue_row["price"].iloc[0]
    if not previous_revenue_row.empty
    else 0
)


# ============================================================
# LATEST ORDERS
# ============================================================

latest_orders_row = monthly_orders[
    monthly_orders["month"]
    == latest_signal_month
]

latest_orders = (
    latest_orders_row["orders"].iloc[0]
    if not latest_orders_row.empty
    else 0
)


# ============================================================
# LATEST AOV
# ============================================================

latest_aov = (
    latest_revenue / latest_orders
    if latest_orders > 0
    else 0
)


# ============================================================
# LATEST RATING
# ============================================================

latest_rating_row = monthly_rating[
    monthly_rating["month"]
    == latest_signal_month
]

latest_rating = (
    latest_rating_row[
        "avg_rating"
    ].iloc[0]
    if not latest_rating_row.empty
    else None
)


# ============================================================
# SIGNAL
# ============================================================

signal_status = str(
    signal["signal"]
).strip().upper()


# ============================================================
# DIAGNOSTIC CONFIDENCE
# ============================================================

diagnosis_valid = diagnosis[
    diagnosis["previous_revenue"] > 0
].copy()

meaningful_categories = diagnosis[
    (
        diagnosis["previous_revenue"] > 0
    )
    &
    (
        diagnosis["previous_orders"]
        +
        diagnosis["latest_orders"]
        >= 5
    )
].copy()

if len(diagnosis_valid) == 0:

    evidence_confidence = "LOW"

elif len(meaningful_categories) < 2:

    evidence_confidence = "MEDIUM"

else:

    evidence_confidence = "HIGH"


# ============================================================
# HEADER
# ============================================================

st.markdown(
    f"""
<div class="case-tab">
📁 CASE FILE No. {CASE_ID}
</div>

<div class="hero">

<div class="hero-title">
KPI Storytelling Engine
</div>

<div class="hero-subtitle">
From signal → evidence → explanation → action —
with uncertainty and human accountability built in.
</div>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# KPI CARDS
# ============================================================

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.markdown(
        f"""
<div class="card">
<div class="card-label">
LATEST COMPLETE REVENUE
</div>

<div class="card-value">
₹{latest_revenue:,.0f}
</div>

<div class="card-sub">
{latest_signal_month}
</div>
</div>
""",
        unsafe_allow_html=True
    )


with c2:

    st.markdown(
        f"""
<div class="card">
<div class="card-label">
REVENUE CHANGE
</div>

<div class="card-value">
{signal["latest_change"]:.2f}%
</div>

<div class="card-sub">
{previous_signal_month} → {latest_signal_month}
</div>
</div>
""",
        unsafe_allow_html=True
    )


with c3:

    st.markdown(
        f"""
<div class="card">
<div class="card-label">
ORDERS
</div>

<div class="card-value">
{latest_orders:,.0f}
</div>

<div class="card-sub">
latest complete period
</div>
</div>
""",
        unsafe_allow_html=True
    )


with c4:

    rating_text = (
        f"{latest_rating:.2f} / 5"
        if latest_rating is not None
        else "N/A"
    )

    st.markdown(
        f"""
<div class="card">
<div class="card-label">
CUSTOMER RATING
</div>

<div class="card-value">
{rating_text}
</div>

<div class="card-sub">
average review score
</div>
</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# CASE SUMMARY
# ============================================================

st.markdown(
    """
<div class="section-eyebrow">
Case Summary
</div>

<div class="section-title">
📖 Executive Story
</div>

<div class="section-caption">
A deterministic evidence chain converts KPI movement into
an investigation-ready narrative.
</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# TOP CATEGORY
# ============================================================

declining_categories = diagnosis[
    diagnosis["revenue_change"] < 0
].copy()

meaningful_declines = declining_categories[
    declining_categories["previous_revenue"] > 0
].copy()

meaningful_declines = meaningful_declines.sort_values(
    "revenue_change"
)


if not meaningful_declines.empty:

    top_category_row = meaningful_declines.iloc[0]

    top_category = top_category_row[
        "product_category_name"
    ]

    top_category_change = top_category_row[
        "percentage_change"
    ]

    top_category_status = top_category_row[
        "evidence_status"
    ]

else:

    top_category = (
        "No material declining category identified"
    )

    top_category_change = 0

    top_category_status = "NONE"


# ============================================================
# TOP THEME
# ============================================================

top_theme = (
    max(themes, key=themes.get)
    if themes
    else "No dominant theme"
)


# ============================================================
# STORY
# ============================================================

story = (
    f"Revenue changed by "
    f"<b>{signal['latest_change']:.2f}%</b> "
    f"in <b>{latest_signal_month}</b>. "
    f"The Signal Agent classifies this as "
    f"<b>{signal['signal'].lower()}</b>. "
)


if not meaningful_declines.empty:

    story += (
        f"The largest observed category movement is "
        f"<b>{top_category}</b>, at "
        f"<b>{top_category_change:.1f}%</b>. "
    )

    if top_category_status.startswith(
        "DISCONTINUITY"
    ):

        story += (
            "However, this category shows a potential "
            "<b>sales discontinuity</b>, so the movement "
            "should be validated before being treated as "
            "a business cause. "
        )


story += (
    f"Across the available negative customer feedback, "
    f"<b>{top_theme.lower()}</b> is the leading theme. "
    f"This is evidence for investigation, not proof of causation."
)


st.markdown(
    f"""
<div class="story">

<div class="story-label">
Filed Evidence — Read Before Acting
</div>

<div class="story-text">
{story}
</div>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# CONFIDENCE
# ============================================================

if evidence_confidence == "LOW":

    st.warning(
        "LOW CONFIDENCE — Evidence is insufficient to support "
        "a specific category-level action. The engine recommends "
        "additional investigation rather than asserting a cause."
    )

elif evidence_confidence == "MEDIUM":

    st.info(
        "MEDIUM CONFIDENCE — Category-level evidence exists, "
        "but data coverage or comparability limits causal "
        "interpretation."
    )

else:

    st.success(
        "HIGH EVIDENCE COVERAGE — Multiple comparable category "
        "movements are available. Causality still requires "
        "business validation."
    )


# ============================================================
# EXHIBIT A
# ============================================================

st.markdown(
    """
<div class="section-eyebrow">
Exhibit A
</div>

<div class="section-title">
📈 Revenue Trend
</div>

<div class="section-caption">
Completed monthly periods used by the Signal Agent.
</div>
""",
    unsafe_allow_html=True
)


chart_data = monthly_revenue[
    monthly_revenue["month"]
    <= latest_signal_month
].copy()

chart_data["month"] = (
    chart_data["month"].astype(str)
)

chart_data = chart_data.rename(
    columns={
        "price": "Revenue (₹)"
    }
)

chart_data = chart_data.set_index(
    "month"
)

st.line_chart(
    chart_data["Revenue (₹)"],
    height=320
)


# ============================================================
# EXHIBIT B + C
# ============================================================

left, right = st.columns(2)


with left:

    st.markdown(
        """
<div class="section-eyebrow">
Exhibit B
</div>

<div class="section-title">
🔎 Signal Agent
</div>
""",
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
<div class="agent">

<div class="exhibit-tag">
STATISTICAL TEST
</div>

<div class="agent-name">
Is the movement statistically unusual?
</div>

<div class="agent-text">

<b>Latest complete month:</b>
{signal["latest_month"]}
<br><br>

<b>Latest change:</b>
{signal["latest_change"]:.2f}%
<br><br>

<b>Historical mean:</b>
{signal["historical_mean"]:.2f}%
<br><br>

<b>Historical standard deviation:</b>
{signal["historical_std"]:.2f}
<br><br>

<b>Z-score:</b>
{signal["z_score"]:.2f}
<br><br>

<b>Historical observations:</b>
{signal["historical_periods"]}
<br><br>

<b>Verdict:</b>
{signal["signal"]}

</div>

</div>
""",
        unsafe_allow_html=True
    )


with right:

    st.markdown(
        """
<div class="section-eyebrow">
Exhibit C
</div>

<div class="section-title">
💬 Customer Voice
</div>
""",
        unsafe_allow_html=True
    )

    theme_df = pd.DataFrame(
        list(themes.items()),
        columns=[
            "Theme",
            "Negative Reviews"
        ]
    )

    if not theme_df.empty:

        theme_df = theme_df.sort_values(
            "Negative Reviews",
            ascending=True
        )

        st.bar_chart(
            theme_df.set_index("Theme"),
            height=250
        )

    st.caption(
        "Themes are derived from negative review text using "
        "deterministic keyword matching. They are not linked "
        "to individual revenue categories."
    )


# ============================================================
# EXHIBIT D
# ============================================================

st.markdown(
    f"""
<div class="section-eyebrow">
Exhibit D
</div>

<div class="section-title">
🧠 Diagnostic Agent
</div>

<div class="section-caption">
Category-level revenue evidence:
{previous_month} → {latest_month}.
</div>
""",
    unsafe_allow_html=True
)


display_data = diagnosis[
    [
        "product_category_name",
        "latest_revenue",
        "previous_revenue",
        "revenue_change",
        "percentage_change",
        "decline_contribution",
        "evidence_status"
    ]
].head(12).copy()


display_data.columns = [
    "Category",
    "Latest Revenue",
    "Previous Revenue",
    "Revenue Change",
    "% Change",
    "Decline Contribution",
    "Evidence Status"
]


def color_change(value):

    try:

        if float(value) < 0:
            return (
                "color: #e08a7d; "
                "font-weight: 600;"
            )

        return (
            "color: #9dc191; "
            "font-weight: 600;"
        )

    except Exception:

        return ""


styled_table = (
    display_data.style
    .format(
        {
            "Latest Revenue": "₹{:,.0f}",
            "Previous Revenue": "₹{:,.0f}",
            "Revenue Change": "₹{:,.0f}",
            "% Change": (
                lambda x:
                "N/A"
                if pd.isna(x)
                else f"{x:.1f}%"
            ),
            "Decline Contribution": "{:.1f}%"
        }
    )
    .map(
        color_change,
        subset=[
            "Revenue Change",
            "% Change"
        ]
    )
)


st.dataframe(
    styled_table,
    width="stretch",
    hide_index=True
)


# ============================================================
# DECISION WORKSPACE
# ============================================================

st.markdown(
    """
<div class="section-eyebrow">
Decision Workspace
</div>

<div class="section-title">
🔬 Investigate a Category
</div>

<div class="section-caption">
Move from aggregate KPI movement to a specific business
driver without inventing causal relationships.
</div>
""",
    unsafe_allow_html=True
)


available_categories = (
    diagnosis[
        "product_category_name"
    ]
    .dropna()
    .astype(str)
    .tolist()
)


if available_categories:

    declining_names = (
        meaningful_declines[
            "product_category_name"
        ]
        .astype(str)
        .tolist()
    )

    default_category = (
        declining_names[0]
        if declining_names
        else available_categories[0]
    )

    default_index = (
        available_categories.index(
            default_category
        )
    )

    selected_category = st.selectbox(
        "Select a category to investigate",
        available_categories,
        index=default_index
    )

    selected_rows = diagnosis[
        diagnosis[
            "product_category_name"
        ]
        == selected_category
    ]

    if not selected_rows.empty:

        selected = selected_rows.iloc[0]

        selected_latest = selected[
            "latest_revenue"
        ]

        selected_previous = selected[
            "previous_revenue"
        ]

        selected_change = selected[
            "revenue_change"
        ]

        selected_pct = selected[
            "percentage_change"
        ]

        selected_status = selected[
            "evidence_status"
        ]

        selected_contribution = selected[
            "decline_contribution"
        ]

        decline_rank = selected.get(
            "decline_rank",
            pd.NA
        )

        if pd.isna(decline_rank):

            rank_display = "—"

        else:

            rank_display = (
                f"#{int(decline_rank)}"
            )

        # --------------------------------------------------------
        # Investigation
        # --------------------------------------------------------

        st.markdown(
            '<div class="investigation">',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
<div class="investigation-title">
Category Investigation — {selected_category}
</div>
""",
            unsafe_allow_html=True
        )

        m1, m2, m3, m4 = st.columns(4)

        with m1:

            st.markdown(
                f"""
<div class="evidence-box">

<div class="evidence-label">
Latest Revenue
</div>

<div class="investigation-value">
₹{selected_latest:,.0f}
</div>

</div>
""",
                unsafe_allow_html=True
            )

        with m2:

            st.markdown(
                f"""
<div class="evidence-box">

<div class="evidence-label">
Revenue Change
</div>

<div class="investigation-value">
₹{selected_change:,.0f}
</div>

</div>
""",
                unsafe_allow_html=True
            )

        with m3:

            pct_display = (
                f"{selected_pct:.1f}%"
                if pd.notna(selected_pct)
                else "N/A"
            )

            st.markdown(
                f"""
<div class="evidence-box">

<div class="evidence-label">
% Change
</div>

<div class="investigation-value">
{pct_display}
</div>

</div>
""",
                unsafe_allow_html=True
            )

        with m4:

            st.markdown(
                f"""
<div class="evidence-box">

<div class="evidence-label">
Decline Rank
</div>

<div class="investigation-value">
{rank_display}
</div>

</div>
""",
                unsafe_allow_html=True
            )

        st.markdown(
            "<br>",
            unsafe_allow_html=True
        )

        e1, e2 = st.columns(2)

        with e1:

            st.markdown(
                f"""
<div class="evidence-box">

<div class="evidence-label">
Evidence
</div>

<div class="evidence-text">

<b>Revenue:</b>
₹{selected_previous:,.0f}
→
₹{selected_latest:,.0f}

<br><br>

<b>Absolute impact:</b>
₹{selected_change:,.0f}

<br><br>

<b>Share of observed category decline:</b>
{selected_contribution:.1f}%

<br><br>

<b>Previous orders:</b>
{int(selected["previous_orders"]):,}

<br><br>

<b>Latest orders:</b>
{int(selected["latest_orders"]):,}

<br><br>

<b>Evidence status:</b>
{selected_status}

</div>

</div>
""",
                unsafe_allow_html=True
            )

        with e2:

            if selected_status.startswith(
                "DISCONTINUITY"
            ):

                next_step = (
                    f"{selected_category} shows a large "
                    "revenue discontinuity. Validate inventory, "
                    "catalog availability and order records "
                    "before attributing the movement to customer "
                    "or product behavior."
                )

            elif selected_change < 0:

                next_step = (
                    f"Investigate {selected_category} first. "
                    "Validate product, order and delivery evidence "
                    "before taking corrective action."
                )

            else:

                next_step = (
                    f"{selected_category} is not currently "
                    "a declining category and should not be "
                    "treated as the primary driver."
                )

            st.markdown(
                f"""
<div class="evidence-box">

<div class="evidence-label">
Recommended Next Step
</div>

<div class="evidence-text">

{next_step}

<br><br>

<b>Important:</b>

Customer-review themes are measured across the available "
"review population. They are not currently linked to this "
"category, so the pipeline does not establish a "
"category-specific causal relationship.

</div>

</div>
""",
                unsafe_allow_html=True
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


# ============================================================
# EXHIBIT E — STRATEGIST
# ============================================================

st.markdown(
    """
<div class="section-eyebrow">
Exhibit E
</div>

<div class="section-title">
🎯 Strategist Agent
</div>
""",
    unsafe_allow_html=True
)


st.markdown(
    f"""
<div class="recommendation">

<div class="recommendation-title">
Recommended Next Step
</div>

<div class="recommendation-text">
{strategy["recommendation"]}
</div>

<br>

<span class="meta-label">
Why
</span>

<br>

{strategy["reason"]}

<br><br>

<span class="meta-label">
Confidence
</span>

<br>

{strategy["confidence"]}

<br><br>

<span class="meta-label">
Decision Status
</span>

<br>

{strategy["decision_status"]}

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# PERSONA VIEWS
# ============================================================

st.markdown(
    """
<div class="section-eyebrow">
Personalized Intelligence
</div>

<div class="section-title">
👥 Same Evidence, Different Decision Context
</div>

<div class="section-caption">
The analytical evidence stays fixed while the narrative
changes according to decision rights.
</div>
""",
    unsafe_allow_html=True
)


persona = st.radio(
    "View insight as",
    [
        "Executive",
        "Analyst"
    ],
    horizontal=True
)


if persona == "Executive":

    executive_text = (
        f"Revenue moved "
        f"{signal['latest_change']:.1f}% in "
        f"{latest_signal_month} and the movement is "
        f"classified as {signal['signal'].lower()}. "
    )

    if not meaningful_declines.empty:

        executive_text += (
            f"The largest observed category movement is "
            f"{top_category}, at "
            f"{top_category_change:.1f}%. "
        )

    executive_text += (
        "The recommended decision is to validate the "
        "leading evidence before committing pricing, "
        "inventory or promotional resources."
    )

    st.markdown(
        f"""
<div class="agent">

<div class="exhibit-tag">
EXECUTIVE VIEW
</div>

<div class="agent-name">
What does leadership need to know?
</div>

<div class="agent-text">
{executive_text}
</div>

</div>
""",
        unsafe_allow_html=True
    )

else:

    analyst_text = (
        f"Signal z-score: "
        f"{signal['z_score']:.2f}. "
        f"Latest change: "
        f"{signal['latest_change']:.2f}%. "
        f"Historical mean: "
        f"{signal['historical_mean']:.2f}%. "
        f"Diagnostic evidence contains "
        f"{len(diagnosis_valid)} categories with "
        "previous-period revenue. "
        "Review evidence is summarized at aggregate "
        "theme level."
    )

    st.markdown(
        f"""
<div class="agent">

<div class="exhibit-tag">
ANALYST VIEW
</div>

<div class="agent-name">
What should be validated?
</div>

<div class="agent-text">

{analyst_text}

<br><br>

<b>Suggested validation:</b>

Examine category-level order volume,
fulfillment performance, pricing/mix and
review evidence before asserting causality.

</div>

</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# GOVERNANCE
# ============================================================

st.markdown(
    """
<div class="section-eyebrow">
Governance
</div>

<div class="section-title">
🧾 KPI Contract & Lineage
</div>

<div class="section-caption">
Every insight begins with deterministic transformations
before the agent layer organizes the evidence.
</div>
""",
    unsafe_allow_html=True
)


lineage_df = pd.DataFrame(
    [
        [
            "Revenue",
            "Σ item price by order/month",
            "Orders + Items",
            "Deterministic aggregation"
        ],
        [
            "Orders",
            "Count orders by month",
            "Orders",
            "Deterministic aggregation"
        ],
        [
            "AOV",
            "Revenue / Orders",
            "Orders + Items",
            "Deterministic calculation"
        ],
        [
            "Customer Rating",
            "Mean review score",
            "Reviews + Orders",
            "Deterministic aggregation"
        ],
        [
            "Revenue Signal",
            "Latest change vs historical distribution",
            "Revenue KPI",
            "Z-score statistical test"
        ],
        [
            "Category Driver",
            "Latest vs previous category revenue",
            "Orders + Items + Products",
            "Contribution analysis"
        ],
        [
            "Customer Voice",
            "Negative review keyword themes",
            "Reviews",
            "Deterministic text classification"
        ]
    ],
    columns=[
        "KPI / Insight",
        "Definition",
        "Sources",
        "Method"
    ]
)


st.dataframe(
    lineage_df,
    width="stretch",
    hide_index=True
)


# ============================================================
# METHOD
# ============================================================

with st.expander(
    "⚙️ How the engine works"
):

    st.markdown(
        """
### Analytical pipeline

**1. Deterministic data layer**

- Revenue is calculated from order items.
- Orders are counted from order records.
- AOV is calculated from revenue / orders.
- Customer rating is calculated from reviews.

**2. Signal Agent**

- Calculates month-over-month revenue movement.
- Uses only completed monthly periods.
- Compares the latest movement against a historical baseline.
- Uses a z-score to identify unusual movements.

**3. Diagnostic Agent**

- Compares category revenue between completed periods.
- Measures absolute and percentage movement.
- Calculates category contribution.
- Checks order volume and category history.
- Flags potential discontinuities and sparse categories.
- Separately summarizes negative customer-review themes.

**4. Strategist Agent**

- Converts evidence into a recommended next step.
- Can monitor, investigate, validate or abstain.
- Does not create quantitative facts.

**5. Human decision**

- The recommendation remains reviewable and overridable.
- The engine does not automatically execute business decisions.
- Causality is not claimed without supporting evidence.

### Agent architecture

The prototype implements the agent roles as deterministic
decision modules.

This ensures that quantitative outputs remain reproducible,
traceable and auditable.

The architecture is intentionally designed so that an LLM can
later be introduced for narrative generation without allowing
the model to become the source of quantitative truth.
"""
    )

st.markdown("## 🤖 Agent Architecture")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 01 · Signal Agent")
    st.write(
        "Detects whether the latest KPI movement "
        "is statistically unusual relative to history."
    )

with col2:
    st.markdown("### 02 · Diagnostic Agent")
    st.write(
        "Identifies category-level evidence and "
        "checks whether apparent drivers require validation."
    )

with col3:
    st.markdown("### 03 · Strategist Agent")
    st.write(
        "Converts evidence into a decision state: "
        "MONITOR, VALIDATE, INVESTIGATE or ABSTAIN."
    )

st.markdown(
    "**Signal → Evidence → Explanation → Action → Human Review**"
)

# ============================================================
# DATA FRESHNESS
# ============================================================

st.markdown(
    """
<div class="section-eyebrow">
Data Operations
</div>

<div class="section-title">
🕐 Source Freshness
</div>
""",
    unsafe_allow_html=True
)


source_df = pd.DataFrame(
    [
        [
            "Orders",
            str(
                orders[
                    "order_purchase_timestamp"
                ].max().date()
            ),
            f"{len(orders):,}",
            "Available"
        ],
        [
            "Order Items",
            "Linked to order records",
            f"{len(items):,}",
            "Available"
        ],
        [
            "Products",
            "Linked to product records",
            f"{len(products):,}",
            "Available"
        ],
        [
            "Reviews",
            "Linked to order records",
            f"{len(reviews):,}",
            "Available"
        ]
    ],
    columns=[
        "Source",
        "Latest Data",
        "Rows",
        "Status"
    ]
)


st.dataframe(
    source_df,
    width="stretch",
    hide_index=True
)


# ============================================================
# LEARNING LOOP — ANALYST FEEDBACK
# ============================================================

st.markdown("## ✍️ Analyst Feedback")

st.markdown(
    """
    <div class="section-subtitle">
        Prototype mechanism for capturing analyst corrections
        and overrides for future evaluation.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("### How useful was this recommendation?")

feedback = st.radio(
    "Recommendation feedback",
    ["👍 Useful", "👎 Not useful"],
    horizontal=True,
    key="recommendation_feedback"
)

correction = st.text_area(
    "Optional correction or comment",
    placeholder="Example: Inventory was unavailable in this category.",
    key="analyst_correction"
)

if st.button("Submit Feedback", type="primary"):

    feedback_record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "case": "KPI-2026-08",
        "feedback": feedback,
        "correction": correction
    }

    if "feedback_records" not in st.session_state:
        st.session_state.feedback_records = []

    st.session_state.feedback_records.append(
        feedback_record
    )

    st.success(
        "Feedback captured successfully for future evaluation."
    )

# ------------------------------------------------------------
# FEEDBACK SUMMARY
# ------------------------------------------------------------

feedback_records = st.session_state.get(
    "feedback_records",
    []
)

useful_count = sum(
    1
    for record in feedback_records
    if record["feedback"] == "👍 Useful"
)

not_useful_count = sum(
    1
    for record in feedback_records
    if record["feedback"] == "👎 Not useful"
)

correction_count = sum(
    1
    for record in feedback_records
    if record["correction"].strip()
)

st.markdown("### Learning Loop")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Feedback captured",
        len(feedback_records)
    )

with col2:
    st.metric(
        "Useful",
        useful_count
    )

with col3:
    st.metric(
        "Corrections",
        correction_count
    )

st.caption(
    "Analyst feedback is captured for future evaluation "
    "and agent improvement. It does not automatically "
    "change quantitative evidence."
)

# ============================================================
# TELEMETRY
# ============================================================

st.markdown(
    """
<div class="section-eyebrow">
Runtime
</div>

<div class="section-title">
📊 Engine Telemetry
</div>
""",
    unsafe_allow_html=True
)


telemetry_cols = st.columns(4)


with telemetry_cols[0]:

    st.markdown(
        f"""
<div class="card">

<div class="card-label">
PIPELINE LATENCY
</div>

<div class="card-value">
{pipeline_latency:.2f}s
</div>

<div class="card-sub">
data → recommendation
</div>

</div>
""",
        unsafe_allow_html=True
    )


with telemetry_cols[1]:

    st.markdown(
        """
<div class="card">

<div class="card-label">
AGENT MODULES
</div>

<div class="card-value">
3
</div>

<div class="card-sub">
Signal · Diagnostic · Strategist
</div>

</div>
""",
        unsafe_allow_html=True
    )


with telemetry_cols[2]:

    st.markdown(
        """
<div class="card">

<div class="card-label">
QUANTITATIVE MODEL CALLS
</div>

<div class="card-value">
0
</div>

<div class="card-sub">
deterministic evidence layer
</div>

</div>
""",
        unsafe_allow_html=True
    )


with telemetry_cols[3]:

    st.markdown(
        f"""
<div class="card">

<div class="card-label">
EVIDENCE CONFIDENCE
</div>

<div class="card-value">
{evidence_confidence}
</div>

<div class="card-sub">
based on evidence coverage
</div>

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

<div class="human-title">
✍️ Human Sign-off
</div>

<div class="human-text">

The engine detects, diagnoses and recommends —
but it does not automatically execute business decisions.

Quantitative evidence remains deterministic and traceable,
while recommendations remain reviewable, overridable and
accountable to a human decision-maker.

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
font-family:'IBM Plex Mono',monospace;
font-size:11px;
letter-spacing:1px;
">

KPI STORYTELLING ENGINE · CASE {CASE_ID}
· EVIDENCE BEFORE ACTION

</div>
""",
    unsafe_allow_html=True
)