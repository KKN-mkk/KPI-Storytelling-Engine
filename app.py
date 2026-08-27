import time
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

CASE_ID = "KPI-2026-08"


# ============================================================
# DESIGN TOKENS & STYLES
# ============================================================

st.markdown("""
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

/* ============================================================
   HEADER
   ============================================================ */

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
    padding: 8px 16px;
    border-radius: 0 0 10px 10px;
    margin-bottom: 0;
}

.hero {
    border: 1px solid var(--line);
    border-top: none;
    border-radius: 0 12px 12px 12px;
    background: linear-gradient(180deg, var(--panel-2), var(--panel));
    padding: 32px 36px 30px 36px;
    margin-bottom: 40px;
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

/* ============================================================
   SECTION HEADINGS
   ============================================================ */

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

/* ============================================================
   CARDS
   ============================================================ */

.card {
    position: relative;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 4px 10px 10px 10px;
    padding: 18px 20px;
    height: 100%;
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
    background: linear-gradient(180deg, var(--panel), var(--panel-2));
    border: 1px solid var(--line);
    border-left: 4px solid var(--brick);
    border-radius: 4px 10px 10px 4px;
    padding: 28px 32px;
    margin-top: 8px;
    margin-bottom: 8px;
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
   AGENT
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
    margin-bottom: 10px;
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
   INVESTIGATION PANEL
   ============================================================ */

.investigation {
    background: linear-gradient(180deg, var(--panel-2), var(--panel));
    border: 1px solid var(--line);
    border-left: 4px solid var(--paper);
    border-radius: 4px 10px 10px 4px;
    padding: 26px 28px;
    margin-top: 10px;
}

.investigation-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1.4px;
    color: var(--paper);
    text-transform: uppercase;
    margin-bottom: 12px;
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
    display: flex;
    gap: 14px;
    align-items: flex-start;
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

/* ============================================================
   TABLE
   ============================================================ */

[data-testid="stDataFrame"] {
    border: 1px solid var(--line);
    border-radius: 10px;
    overflow: hidden;
    background: var(--panel);
}

</style>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">

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
# DATA PREPARATION
# ============================================================

orders = orders.copy()
items = items.copy()
products = products.copy()
reviews = reviews.copy()

orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"]
)

orders["month"] = orders[
    "order_purchase_timestamp"
].dt.to_period("M")


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
# OTHER BUSINESS KPIs
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
    / monthly_aov["orders"].replace(0, pd.NA)
)


# ============================================================
# CUSTOMER RATING KPI
# ============================================================

review_kpi = reviews.merge(
    orders[["order_id", "month"]],
    on="order_id",
    how="inner"
)

monthly_rating = (
    review_kpi.groupby("month")["review_score"]
    .mean()
    .reset_index(name="avg_rating")
)


# ============================================================
# AGENT PIPELINE
# ============================================================

pipeline_start = time.perf_counter()

signal = detect_signal(monthly_revenue)

diagnosis, latest_month, previous_month, themes = (
    diagnose_revenue_change(
        orders,
        items,
        products,
        reviews
    )
)

strategy = generate_strategy(
    signal,
    diagnosis,
    themes,
    latest_month,
    previous_month
)

pipeline_latency = time.perf_counter() - pipeline_start


# ============================================================
# LATEST KPI VALUES
# ============================================================

latest_revenue_row = monthly_revenue[
    monthly_revenue["month"] == signal["latest_month"]
]

previous_revenue_row = monthly_revenue[
    monthly_revenue["month"] == previous_month
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

latest_orders_row = monthly_orders[
    monthly_orders["month"] == signal["latest_month"]
]

latest_orders = (
    latest_orders_row["orders"].iloc[0]
    if not latest_orders_row.empty
    else 0
)

latest_aov = (
    latest_revenue / latest_orders
    if latest_orders > 0
    else 0
)

latest_rating_row = monthly_rating[
    monthly_rating["month"] == signal["latest_month"]
]

latest_rating = (
    latest_rating_row["avg_rating"].iloc[0]
    if not latest_rating_row.empty
    else None
)


# ============================================================
# SIGNAL STATUS
# ============================================================

signal_status = str(
    signal["signal"]
).strip().upper()

is_alert = signal_status == "SIGNIFICANT CHANGE"


# ============================================================
# DATA QUALITY / CONFIDENCE
# ============================================================

diagnosis_valid = diagnosis[
    diagnosis["previous_revenue"] > 0
].copy()

declining_categories = diagnosis_valid[
    diagnosis_valid["revenue_change"] < 0
].copy()

if len(diagnosis_valid) == 0:

    evidence_confidence = "LOW"

elif len(declining_categories) < 2:

    evidence_confidence = "MEDIUM"

else:

    evidence_confidence = "HIGH"


# ============================================================
# HEADER
# ============================================================

st.markdown(f"""
<div class="case-tab">
📁 CASE FILE No. {CASE_ID}
</div>

<div class="hero">

<div class="hero-title">
KPI Storytelling Engine
</div>

<div class="hero-subtitle">
From signal → evidence → explanation → action — with uncertainty and human accountability built in.
</div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# KPI CARDS
# ============================================================

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.markdown(f"""
    <div class="card">
        <div class="card-label">LATEST REVENUE</div>
        <div class="card-value">₹{latest_revenue:,.0f}</div>
        <div class="card-sub">{signal["latest_month"]}</div>
    </div>
    """, unsafe_allow_html=True)


with c2:

    st.markdown(f"""
    <div class="card">
        <div class="card-label">REVENUE CHANGE</div>
        <div class="card-value">{signal["latest_change"]:.2f}%</div>
        <div class="card-sub">{previous_month} → {signal["latest_month"]}</div>
    </div>
    """, unsafe_allow_html=True)


with c3:

    st.markdown(f"""
    <div class="card">
        <div class="card-label">ORDERS</div>
        <div class="card-value">{latest_orders:,.0f}</div>
        <div class="card-sub">latest complete period</div>
    </div>
    """, unsafe_allow_html=True)


with c4:

    rating_text = (
        f"{latest_rating:.2f} / 5"
        if latest_rating is not None
        else "N/A"
    )

    st.markdown(f"""
    <div class="card">
        <div class="card-label">CUSTOMER RATING</div>
        <div class="card-value">{rating_text}</div>
        <div class="card-sub">average review score</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# CASE SUMMARY
# ============================================================

st.markdown(
    '<div class="section-eyebrow">Case Summary</div>'
    '<div class="section-title">📖 Executive Story</div>'
    '<div class="section-caption">'
    'A deterministic analytical chain converts the KPI movement into an evidence-backed narrative.'
    '</div>',
    unsafe_allow_html=True
)


if not declining_categories.empty:

    top_category_row = declining_categories.iloc[0]

    top_category = top_category_row[
        "product_category_name"
    ]

    top_category_change = top_category_row[
        "percentage_change"
    ]

else:

    top_category = "No material declining category identified"
    top_category_change = 0


top_theme = (
    max(themes, key=themes.get)
    if themes
    else "No dominant theme"
)


story = (
    f"Revenue changed by <b>{signal['latest_change']:.2f}%</b> "
    f"in {signal['latest_month']}. The Signal Agent classifies "
    f"this as <b>{signal['signal'].lower()}</b>. "
)

if not declining_categories.empty:

    story += (
        f"The largest category-level decline is "
        f"<b>{top_category}</b>, down "
        f"<b>{top_category_change:.1f}%</b>. "
    )

story += (
    f"Across the available customer feedback, "
    f"<b>{top_theme.lower()}</b> is the leading review theme. "
    f"This is evidence for investigation, not proof of causation."
)


st.markdown(f"""
<div class="story">

<div class="story-label">
Filed Evidence — Read Before Acting
</div>

<div class="story-text">
{story}
</div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# CONFIDENCE / ABSTENTION
# ============================================================

if evidence_confidence == "LOW":

    st.warning(
        "LOW CONFIDENCE — Evidence is insufficient to support a "
        "specific category-level action. The engine recommends "
        "additional investigation rather than asserting a cause."
    )

elif evidence_confidence == "MEDIUM":

    st.info(
        "MEDIUM CONFIDENCE — A category movement is visible, "
        "but the available evidence does not establish causality."
    )

else:

    st.success(
        "HIGH EVIDENCE COVERAGE — Multiple category movements "
        "are available for comparison. Causality still requires validation."
    )


# ============================================================
# EXHIBIT A — REVENUE TREND
# ============================================================

st.markdown(
    '<div class="section-eyebrow">Exhibit A</div>'
    '<div class="section-title">📈 Revenue Trend</div>'
    '<div class="section-caption">'
    'Completed monthly periods used by the Signal Agent.'
    '</div>',
    unsafe_allow_html=True
)


chart_data = monthly_revenue[
    monthly_revenue["month"] <= signal["latest_month"]
].copy()

chart_data["month"] = chart_data["month"].astype(str)

chart_data = chart_data.rename(
    columns={"price": "Revenue (₹)"}
)

chart_data = chart_data.set_index("month")

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
        '<div class="section-eyebrow">Exhibit B</div>'
        '<div class="section-title">🔎 Signal Agent</div>',
        unsafe_allow_html=True
    )

    st.markdown(f"""
    <div class="agent">

    <div class="exhibit-tag">
    STATISTICAL TEST
    </div>

    <div class="agent-name">
    Is the movement statistically unusual?
    </div>

    <div class="agent-text">

    <b>Latest change:</b>
    {signal["latest_change"]:.2f}%<br><br>

    <b>Historical mean:</b>
    {signal["historical_mean"]:.2f}%<br><br>

    <b>Historical standard deviation:</b>
    {signal["historical_std"]:.2f}<br><br>

    <b>Z-score:</b>
    {signal["z_score"]:.2f}<br><br>

    <b>Verdict:</b>
    {signal["signal"]}

    </div>

    </div>
    """, unsafe_allow_html=True)


with right:

    st.markdown(
        '<div class="section-eyebrow">Exhibit C</div>'
        '<div class="section-title">💬 Customer Voice</div>',
        unsafe_allow_html=True
    )

    theme_df = pd.DataFrame(
        list(themes.items()),
        columns=["Theme", "Negative Reviews"]
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
        "Themes are derived from negative review text using deterministic "
        "keyword matching. They are not linked to individual revenue categories."
    )


# ============================================================
# EXHIBIT D — DIAGNOSTIC AGENT
# ============================================================

st.markdown(
    '<div class="section-eyebrow">Exhibit D</div>'
    '<div class="section-title">🧠 Diagnostic Agent</div>'
    f'<div class="section-caption">'
    f'Category-level revenue contribution: {previous_month} → {latest_month}.'
    f'</div>',
    unsafe_allow_html=True
)


display_data = diagnosis[
    [
        "product_category_name",
        "latest_revenue",
        "previous_revenue",
        "revenue_change",
        "percentage_change"
    ]
].head(10).copy()


display_data.columns = [
    "Category",
    "Latest Revenue",
    "Previous Revenue",
    "Revenue Change",
    "% Change"
]


def color_change(value):

    if value < 0:

        return "color: #e08a7d; font-weight: 600;"

    return "color: #9dc191; font-weight: 600;"


styled_table = (
    display_data.style
    .format({
        "Latest Revenue": "₹{:,.0f}",
        "Previous Revenue": "₹{:,.0f}",
        "Revenue Change": "₹{:,.0f}",
        "% Change": "{:.1f}%"
    })
    .map(
        color_change,
        subset=["Revenue Change", "% Change"]
    )
)


st.dataframe(
    styled_table,
    width="stretch",
    hide_index=True
)


# ============================================================
# INVESTIGATE CATEGORY
# ============================================================

st.markdown(
    '<div class="section-eyebrow">Decision Workspace</div>'
    '<div class="section-title">🔬 Investigate a Category</div>'
    '<div class="section-caption">'
    'Move from the aggregate KPI to a specific business driver without inventing causal relationships.'
    '</div>',
    unsafe_allow_html=True
)


available_categories = (
    diagnosis["product_category_name"]
    .dropna()
    .astype(str)
    .tolist()
)


if available_categories:

    # Default to the largest declining category
    declining_names = (
        declining_categories
        .sort_values("revenue_change")
        ["product_category_name"]
        .astype(str)
        .tolist()
    )

    default_category = (
        declining_names[0]
        if declining_names
        else available_categories[0]
    )

    default_index = available_categories.index(default_category)

    selected_category = st.selectbox(
        "Select a category to investigate",
        available_categories,
        index=default_index
    )

    selected_rows = diagnosis[
        diagnosis["product_category_name"]
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

        category_rank = (
            diagnosis_valid[
                diagnosis_valid["revenue_change"] < 0
            ]
            .sort_values("revenue_change")
            .reset_index(drop=True)
        )

        rank_matches = category_rank[
            category_rank["product_category_name"]
            == selected_category
        ]

        if not rank_matches.empty:

            decline_rank = (
                rank_matches.index[0] + 1
            )

        else:

            decline_rank = None

        # Revenue contribution to total decline

        total_decline = abs(
            declining_categories["revenue_change"]
            .sum()
        )

        if (
            selected_change < 0
            and total_decline > 0
        ):

            contribution = (
                abs(selected_change)
                / total_decline
                * 100
            )

        else:

            contribution = 0


        st.markdown(
            '<div class="investigation">',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="investigation-title">'
            f'Category Investigation — {selected_category}'
            f'</div>',
            unsafe_allow_html=True
        )

        m1, m2, m3, m4 = st.columns(4)

        with m1:

            st.markdown(f"""
            <div class="evidence-box">
            <div class="evidence-label">Latest Revenue</div>
            <div class="investigation-value">
            ₹{selected_latest:,.0f}
            </div>
            </div>
            """, unsafe_allow_html=True)

        with m2:

            st.markdown(f"""
            <div class="evidence-box">
            <div class="evidence-label">Revenue Change</div>
            <div class="investigation-value">
            ₹{selected_change:,.0f}
            </div>
            </div>
            """, unsafe_allow_html=True)

        with m3:

            pct_display = (
                f"{selected_pct:.1f}%"
                if pd.notna(selected_pct)
                else "N/A"
            )

            st.markdown(f"""
            <div class="evidence-box">
            <div class="evidence-label">% Change</div>
            <div class="investigation-value">
            {pct_display}
            </div>
            </div>
            """, unsafe_allow_html=True)

        with m4:

            rank_display = (
                f"#{decline_rank}"
                if decline_rank is not None
                else "—"
            )

            st.markdown(f"""
            <div class="evidence-box">
            <div class="evidence-label">Decline Rank</div>
            <div class="investigation-value">
            {rank_display}
            </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        e1, e2 = st.columns(2)

        with e1:

            st.markdown(f"""
            <div class="evidence-box">

            <div class="evidence-label">
            Evidence
            </div>

            <div class="evidence-text">

            <b>Revenue:</b>
            ₹{selected_previous:,.0f}
            → ₹{selected_latest:,.0f}<br><br>

            <b>Absolute impact:</b>
            ₹{selected_change:,.0f}<br><br>

            <b>Share of category decline:</b>
            {contribution:.1f}%<br><br>

            <b>Customer voice:</b>
            {top_theme}

            </div>

            </div>
            """, unsafe_allow_html=True)

        with e2:

            if selected_change < 0:

                next_step = (
                    f"Investigate {selected_category} first. "
                    "Validate whether product, order or delivery "
                    "issues are contributing before taking corrective action."
                )

            else:

                next_step = (
                    f"{selected_category} is not currently a declining "
                    "category. Do not treat it as the primary cause "
                    "of the revenue movement."
                )

            st.markdown(f"""
            <div class="evidence-box">

            <div class="evidence-label">
            Recommended Next Step
            </div>

            <div class="evidence-text">

            {next_step}

            <br><br>

            <b>Important:</b> Customer-review themes are measured
across the available review population. The current
pipeline does not establish a category-specific causal
relationship.

            </div>

            </div>
            """, unsafe_allow_html=True)

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


# ============================================================
# EXHIBIT E — STRATEGIST
# ============================================================

st.markdown(
    '<div class="section-eyebrow">Exhibit E</div>'
    '<div class="section-title">🎯 Strategist Agent</div>',
    unsafe_allow_html=True
)


st.markdown(f"""
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

</div>
""", unsafe_allow_html=True)


# ============================================================
# PERSONA VIEWS
# ============================================================

st.markdown(
    '<div class="section-eyebrow">Personalized Intelligence</div>'
    '<div class="section-title">👥 Same Evidence, Different Decision Context</div>'
    '<div class="section-caption">'
    'The analytical truth stays fixed while the narrative changes according to decision rights.'
    '</div>',
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
        f"Revenue moved {signal['latest_change']:.1f}% in "
        f"{signal['latest_month']} and the movement is classified "
        f"as {signal['signal'].lower()}. "
    )

    if not declining_categories.empty:

        executive_text += (
            f"The largest declining category is "
            f"{top_category}, down "
            f"{top_category_change:.1f}%. "
        )

    executive_text += (
        "The recommended decision is to investigate the leading "
        "driver before committing pricing, inventory or promotional resources."
    )

    st.markdown(f"""
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
    """, unsafe_allow_html=True)


else:

    analyst_text = (
        f"Signal z-score: {signal['z_score']:.2f}. "
        f"Latest change: {signal['latest_change']:.2f}%. "
        f"Historical mean: {signal['historical_mean']:.2f}%. "
        f"Diagnostic evidence contains "
        f"{len(diagnosis_valid)} comparable categories. "
        f"Review evidence is currently summarized at aggregate theme level."
    )

    st.markdown(f"""
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
    Examine category-level order volume, fulfillment performance,
    pricing/mix and review evidence before asserting causality.
    </div>

    </div>
    """, unsafe_allow_html=True)


# ============================================================
# DATA LINEAGE / SEMANTIC CONTRACT
# ============================================================

st.markdown(
    '<div class="section-eyebrow">Governance</div>'
    '<div class="section-title">🧾 KPI Contract & Lineage</div>'
    '<div class="section-caption">'
    'Every insight begins with deterministic data transformations before narrative generation.'
    '</div>',
    unsafe_allow_html=True
)


lineage_df = pd.DataFrame([
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
    ]
], columns=[
    "KPI / Insight",
    "Definition",
    "Sources",
    "Method"
])


st.dataframe(
    lineage_df,
    width="stretch",
    hide_index=True
)


# ============================================================
# METHOD DISCLOSURE
# ============================================================

with st.expander("⚙️ How the engine works"):

    st.markdown("""
    ### Analytical pipeline

    **1. Deterministic data layer**
    - Revenue calculated from order items.
    - Orders counted from order records.
    - AOV calculated from revenue / orders.
    - Customer rating calculated from reviews.

    **2. Signal Agent**
    - Calculates month-over-month revenue movement.
    - Compares the latest movement with historical changes.
    - Uses a z-score to classify unusual movements.

    **3. Diagnostic Agent**
    - Compares category revenue between periods.
    - Ranks declining categories.
    - Separately summarizes negative customer-review themes.

    **4. Strategist Agent**
    - Converts the analytical evidence into a recommended next step.
    - Does not create quantitative facts.

    **5. Human decision**
    - The recommendation remains reviewable and overridable.
    - The engine explicitly avoids claiming causality where evidence is insufficient.

    ### LLM vs non-LLM

    **Non-LLM / deterministic:**
    revenue, orders, AOV, review aggregation, percentage change,
    category contribution, z-score and evidence ranking.

    **Narrative / agent layer:**
    Signal, Diagnostic and Strategist agents organize the evidence
    and communicate it in decision-oriented language.

    **Current prototype principle:**
    The LLM/agent layer is not treated as the source of quantitative truth.
    """)


# ============================================================
# DATA FRESHNESS
# ============================================================

st.markdown(
    '<div class="section-eyebrow">Data Operations</div>'
    '<div class="section-title">🕐 Source Freshness</div>',
    unsafe_allow_html=True
)


source_df = pd.DataFrame([
    [
        "Orders",
        f"{orders['order_purchase_timestamp'].max().date()}",
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
], columns=[
    "Source",
    "Latest Data",
    "Rows",
    "Status"
])


st.dataframe(
    source_df,
    width="stretch",
    hide_index=True
)


# ============================================================
# FEEDBACK LOOP
# ============================================================

st.markdown(
    '<div class="section-eyebrow">Learning Loop</div>'
    '<div class="section-title">✍️ Analyst Feedback</div>'
    '<div class="section-caption">'
    'Prototype mechanism for capturing corrections and overrides for future evaluation.'
    '</div>',
    unsafe_allow_html=True
)


feedback = st.radio(
    "How useful was this recommendation?",
    [
        "Accept recommendation",
        "Needs investigation",
        "Override recommendation"
    ],
    horizontal=True
)


if feedback == "Override recommendation":

    override_reason = st.text_input(
        "Why are you overriding the recommendation?"
    )

else:

    override_reason = ""


if st.button("Record analyst decision"):

    st.session_state["last_feedback"] = {
        "decision": feedback,
        "reason": override_reason,
        "case_id": CASE_ID,
        "timestamp": pd.Timestamp.now().isoformat()
    }

    st.success(
        "Analyst decision recorded for this session. "
        "In production, this event would be persisted to the feedback store."
    )


# ============================================================
# TELEMETRY
# ============================================================

st.markdown(
    '<div class="section-eyebrow">Runtime</div>'
    '<div class="section-title">📊 Engine Telemetry</div>',
    unsafe_allow_html=True
)


telemetry_cols = st.columns(4)

with telemetry_cols[0]:

    st.markdown(f"""
    <div class="card">
    <div class="card-label">PIPELINE LATENCY</div>
    <div class="card-value">{pipeline_latency:.2f}s</div>
    <div class="card-sub">data → recommendation</div>
    </div>
    """, unsafe_allow_html=True)


with telemetry_cols[1]:

    st.markdown("""
    <div class="card">
    <div class="card-label">MODEL CALLS</div>
    <div class="card-value">0</div>
    <div class="card-sub">prototype uses deterministic agents</div>
    </div>
    """, unsafe_allow_html=True)


with telemetry_cols[2]:

    st.markdown("""
    <div class="card">
    <div class="card-label">EST. LLM COST</div>
    <div class="card-value">₹0</div>
    <div class="card-sub">no external LLM call in current pipeline</div>
    </div>
    """, unsafe_allow_html=True)


with telemetry_cols[3]:

    st.markdown(f"""
    <div class="card">
    <div class="card-label">EVIDENCE CONFIDENCE</div>
    <div class="card-value">{evidence_confidence}</div>
    <div class="card-sub">based on available evidence coverage</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# HUMAN IN THE LOOP
# ============================================================

st.markdown("""
<div class="human">

<div class="human-title">
✍️ Human Sign-off
</div>

<div class="human-text">

The engine detects, diagnoses and recommends — but it does not
automatically execute business decisions. Quantitative evidence
remains deterministic and traceable, while recommendations remain
reviewable, overridable and accountable to a human decision-maker.

</div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================

st.markdown(f"""
<br><br>

<div style="
text-align:center;
color:#5b6584;
font-family:'IBM Plex Mono',monospace;
font-size:11px;
letter-spacing:1px;
">

KPI STORYTELLING ENGINE · CASE {CASE_ID} · EVIDENCE BEFORE ACTION

</div>
""", unsafe_allow_html=True)