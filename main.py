import pandas as pd

from agents.signal_agent import detect_signal
from agents.diagnostic_agent import diagnose_revenue_change
from agents.strategist_agent import generate_strategy


# ==========================================
# 1. LOAD DATA
# ==========================================

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


# ==========================================
# 2. CALCULATE MONTHLY REVENUE
# ==========================================

order_revenue = (
    items.groupby("order_id")["price"]
    .sum()
    .reset_index()
)

data = orders.merge(
    order_revenue,
    on="order_id"
)

data["order_purchase_timestamp"] = pd.to_datetime(
    data["order_purchase_timestamp"]
)

data["month"] = (
    data["order_purchase_timestamp"]
    .dt.to_period("M")
)

monthly_revenue = (
    data.groupby("month")["price"]
    .sum()
    .reset_index()
)


# ==========================================
# 3. SIGNAL AGENT
# ==========================================

signal = detect_signal(monthly_revenue)


print("\n================================")
print("      KPI STORYTELLING ENGINE")
print("================================")


print("\nSIGNAL AGENT")
print("--------------------------------")

print(
    "Latest complete month:",
    signal["latest_month"]
)

print(
    "Revenue change:",
    round(signal["latest_change"], 2),
    "%"
)

print(
    "Historical average change:",
    round(signal["historical_mean"], 2),
    "%"
)

print(
    "Historical standard deviation:",
    round(signal["historical_std"], 2)
)

print(
    "Z-score:",
    round(signal["z_score"], 2)
)

print(
    "Signal:",
    signal["signal"]
)


# ==========================================
# 4. DIAGNOSTIC AGENT
# ==========================================

(
    diagnosis,
    latest_month,
    previous_month,
    common_themes
) = diagnose_revenue_change(
    orders,
    items,
    products,
    reviews
)


print("\nDIAGNOSTIC AGENT")
print("--------------------------------")

print(
    "Comparing:",
    previous_month,
    "→",
    latest_month
)

print(
    "\nTop categories contributing to revenue decline:"
)

print(
    diagnosis[
        [
            "product_category_name",
            "latest_revenue",
            "previous_revenue",
            "revenue_change",
            "percentage_change"
        ]
    ]
    .head(10)
    .to_string(index=False)
)


print("\nCUSTOMER REVIEW EVIDENCE")
print("--------------------------------")

print("Negative review themes:")

for theme, count in common_themes.items():

    print(
        f"{theme}: {count} negative reviews"
    )


# ==========================================
# 5. STRATEGIST AGENT
# ==========================================

strategy = generate_strategy(
    signal,
    diagnosis,
    common_themes,
    latest_month,
    previous_month
)


print("\nSTRATEGIST AGENT")
print("--------------------------------")

print(
    "Recommendation:"
)

print(
    strategy["recommendation"]
)

print(
    "\nReason:"
)

print(
    strategy["reason"]
)

print(
    "\nConfidence:",
    strategy["confidence"]
)

print(
    "\nHuman decision required:"
)

print(
    "YES - The recommendation is advisory. "
    "A human makes the final business decision."
)


print("\n================================")
print("        END OF ANALYSIS")
print("================================")