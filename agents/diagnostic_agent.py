import pandas as pd


def diagnose_revenue_change(orders, items, products, reviews):

    orders = orders.copy()

    # -----------------------------
    # DATE PROCESSING
    # -----------------------------

    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"]
    )

    orders["month"] = (
        orders["order_purchase_timestamp"]
        .dt.to_period("M")
    )

    # Remove incomplete month
    monthly_orders = (
        orders.groupby("month")
        .size()
        .reset_index(name="order_count")
    )

    valid_months = monthly_orders[
        monthly_orders["order_count"] >= 1000
    ]["month"]

    orders = orders[
        orders["month"].isin(valid_months)
    ].copy()

    # -----------------------------
    # REVENUE ANALYSIS
    # -----------------------------

    data = orders.merge(
        items[["order_id", "product_id", "price"]],
        on="order_id"
    )

    data = data.merge(
        products[
            ["product_id", "product_category_name"]
        ],
        on="product_id",
        how="left"
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

    latest = monthly_category_revenue[
        monthly_category_revenue["month"] == latest_month
    ].rename(
        columns={"price": "latest_revenue"}
    )

    previous = monthly_category_revenue[
        monthly_category_revenue["month"] == previous_month
    ].rename(
        columns={"price": "previous_revenue"}
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

    comparison = comparison.sort_values(
        "revenue_change"
    )

    # -----------------------------
    # CUSTOMER REVIEW ANALYSIS
    # -----------------------------

    reviews = reviews.copy()

    review_data = reviews.merge(
        orders[["order_id", "month"]],
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

    # Business themes
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

    # Sort themes
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