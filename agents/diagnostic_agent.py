import pandas as pd


def diagnose_revenue_change(orders, items, products, reviews):

    orders = orders.copy()
    items = items.copy()
    products = products.copy()
    reviews = reviews.copy()

    # ============================================================
    # DATE PROCESSING
    # ============================================================

    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"]
    )

    orders["month"] = (
        orders["order_purchase_timestamp"]
        .dt.to_period("M")
    )

    monthly_orders = (
        orders.groupby("month")
        .size()
        .reset_index(name="order_count")
    )

    # Remove potentially incomplete final month.
    latest_raw_month = monthly_orders["month"].max()

    valid_months = monthly_orders[
        monthly_orders["month"] < latest_raw_month
    ]["month"]

    orders = orders[
        orders["month"].isin(valid_months)
    ].copy()

    # ============================================================
    # REVENUE BY CATEGORY
    # ============================================================

    data = orders.merge(
        items[
            ["order_id", "product_id", "price"]
        ],
        on="order_id",
        how="inner"
    )

    data = data.merge(
        products[
            ["product_id", "product_category_name"]
        ],
        on="product_id",
        how="left"
    )

    data["product_category_name"] = (
        data["product_category_name"]
        .fillna("Unknown")
        .astype(str)
    )

    monthly_category_revenue = (
        data.groupby(
            ["month", "product_category_name"]
        )["price"]
        .sum()
        .reset_index()
    )

    latest_month = monthly_category_revenue["month"].max()
    previous_month = latest_month - 1

    latest = (
        monthly_category_revenue[
            monthly_category_revenue["month"] == latest_month
        ]
        .rename(columns={"price": "latest_revenue"})
    )

    previous = (
        monthly_category_revenue[
            monthly_category_revenue["month"] == previous_month
        ]
        .rename(columns={"price": "previous_revenue"})
    )

    comparison = latest.merge(
        previous,
        on="product_category_name",
        how="outer"
    )

    comparison["latest_revenue"] = (
        comparison["latest_revenue"].fillna(0)
    )

    comparison["previous_revenue"] = (
        comparison["previous_revenue"].fillna(0)
    )

    comparison["revenue_change"] = (
        comparison["latest_revenue"]
        - comparison["previous_revenue"]
    )

    comparison["percentage_change"] = (
        comparison["revenue_change"]
        / comparison["previous_revenue"].replace(0, pd.NA)
        * 100
    )

    comparison["absolute_change"] = (
        comparison["revenue_change"].abs()
    )

    comparison = comparison.sort_values(
        "revenue_change"
    ).reset_index(drop=True)

    # ============================================================
    # CONTRIBUTION TO OVERALL DECLINE
    # ============================================================

    total_change = comparison["revenue_change"].sum()

    if total_change < 0:
        comparison["decline_contribution"] = (
            comparison["revenue_change"].clip(upper=0)
            / total_change.abs()
            * 100
        )
    else:
        comparison["decline_contribution"] = 0.0

    declining = comparison[
        comparison["revenue_change"] < 0
    ].copy()

    declining["decline_rank"] = range(
        1,
        len(declining) + 1
    )

    comparison = comparison.merge(
        declining[
            [
                "product_category_name",
                "decline_rank"
            ]
        ],
        on="product_category_name",
        how="left"
    )

    # ============================================================
    # CATEGORY HISTORY
    # ============================================================

    category_history = (
        monthly_category_revenue
        .groupby("product_category_name")["month"]
        .nunique()
        .reset_index(name="history_months")
    )

    comparison = comparison.merge(
        category_history,
        on="product_category_name",
        how="left"
    )

    # ============================================================
    # CUSTOMER REVIEW ANALYSIS
    # ============================================================

    review_data = reviews.merge(
        orders[
            ["order_id", "month"]
        ],
        on="order_id",
        how="inner"
    )

    negative_reviews = review_data[
        review_data["review_score"] <= 2
    ].copy()

    negative_reviews = negative_reviews[
        negative_reviews["review_comment_message"].notna()
    ]

    negative_reviews["text"] = (
        negative_reviews["review_comment_message"]
        .astype(str)
        .str.lower()
    )

    theme_keywords = {

        "Delivery issues": [
            "entrega",
            "entregue",
            "chegou",
            "prazo",
            "atrasado",
            "atraso",
            "demorou"
        ],

        "Product issues": [
            "produto",
            "qualidade",
            "defeito",
            "quebrado",
            "errado"
        ],

        "Order issues": [
            "pedido",
            "comprei",
            "recebi",
            "faltou",
            "cancelado"
        ]
    }

    theme_counts = {}

    for theme, keywords in theme_keywords.items():

        count = 0

        for text in negative_reviews["text"]:

            if any(
                keyword in text
                for keyword in keywords
            ):
                count += 1

        theme_counts[theme] = count

    theme_counts = dict(
        sorted(
            theme_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
    )

    return (
        comparison,
        latest_month,
        previous_month,
        theme_counts
    )