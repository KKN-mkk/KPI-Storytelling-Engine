import pandas as pd


def diagnose_revenue_change(
    orders,
    items,
    products,
    reviews
):
    """
    Diagnostic Agent

    Explains where the revenue movement is concentrated.

    Important principle:
    Category-level movement is evidence for investigation,
    NOT proof of causation.
    """

    orders = orders.copy()
    items = items.copy()
    products = products.copy()
    reviews = reviews.copy()

    # ============================================================
    # DATE PROCESSING
    # ============================================================

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

    monthly_orders = (
        orders.groupby("month")
        .size()
        .reset_index(name="order_count")
    )

    if monthly_orders.empty:
        raise ValueError(
            "No valid order data available."
        )

    # ============================================================
    # REMOVE POTENTIALLY INCOMPLETE FINAL MONTH
    # ============================================================

    latest_raw_month = monthly_orders["month"].max()

    valid_months = monthly_orders.loc[
        monthly_orders["month"] < latest_raw_month,
        "month"
    ]

    orders = orders[
        orders["month"].isin(valid_months)
    ].copy()

    if orders.empty:
        raise ValueError(
            "Not enough complete monthly data available."
        )

    # ============================================================
    # PREPARE ITEM DATA
    # ============================================================

    items["price"] = pd.to_numeric(
        items["price"],
        errors="coerce"
    ).fillna(0)

    # ============================================================
    # REVENUE BY CATEGORY
    # ============================================================

    data = orders.merge(
        items[
            [
                "order_id",
                "product_id",
                "price"
            ]
        ],
        on="order_id",
        how="inner"
    )

    data = data.merge(
        products[
            [
                "product_id",
                "product_category_name"
            ]
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
            [
                "month",
                "product_category_name"
            ]
        )["price"]
        .sum()
        .reset_index()
    )

    if monthly_category_revenue.empty:
        raise ValueError(
            "No category-level revenue could be calculated."
        )

    # ============================================================
    # LATEST / PREVIOUS COMPLETE MONTH
    # ============================================================

    latest_month = (
        monthly_category_revenue["month"].max()
    )

    available_months = sorted(
        monthly_category_revenue["month"].unique()
    )

    earlier_months = [
        m for m in available_months
        if m < latest_month
    ]

    if not earlier_months:
        raise ValueError(
            "No previous month available for comparison."
        )

    previous_month = earlier_months[-1]

    # ============================================================
    # CATEGORY COMPARISON
    # ============================================================

    latest = (
        monthly_category_revenue[
            monthly_category_revenue["month"]
            == latest_month
        ]
        .rename(
            columns={
                "price": "latest_revenue"
            }
        )
    )

    previous = (
        monthly_category_revenue[
            monthly_category_revenue["month"]
            == previous_month
        ]
        .rename(
            columns={
                "price": "previous_revenue"
            }
        )
    )

    comparison = latest.merge(
        previous,
        on="product_category_name",
        how="outer"
    )

    comparison["latest_revenue"] = (
        pd.to_numeric(
            comparison["latest_revenue"],
            errors="coerce"
        )
        .fillna(0)
    )

    comparison["previous_revenue"] = (
        pd.to_numeric(
            comparison["previous_revenue"],
            errors="coerce"
        )
        .fillna(0)
    )

    # ============================================================
    # REVENUE CHANGE
    # ============================================================

    comparison["revenue_change"] = (
        comparison["latest_revenue"]
        - comparison["previous_revenue"]
    )

    comparison["percentage_change"] = (
        comparison["revenue_change"]
        .div(
            comparison["previous_revenue"]
            .replace(0, pd.NA)
        )
        * 100
    )

    comparison["absolute_change"] = (
        comparison["revenue_change"].abs()
    )

    # ============================================================
    # CATEGORY ORDER COUNTS
    # ============================================================

    category_orders_latest = (
        data[
            data["month"] == latest_month
        ]
        .groupby("product_category_name")["order_id"]
        .nunique()
        .reset_index(
            name="latest_orders"
        )
    )

    category_orders_previous = (
        data[
            data["month"] == previous_month
        ]
        .groupby("product_category_name")["order_id"]
        .nunique()
        .reset_index(
            name="previous_orders"
        )
    )

    comparison = comparison.merge(
        category_orders_latest,
        on="product_category_name",
        how="left"
    )

    comparison = comparison.merge(
        category_orders_previous,
        on="product_category_name",
        how="left"
    )

    comparison["latest_orders"] = (
        comparison["latest_orders"]
        .fillna(0)
        .astype(int)
    )

    comparison["previous_orders"] = (
        comparison["previous_orders"]
        .fillna(0)
        .astype(int)
    )

    # ============================================================
    # CATEGORY HISTORY
    # ============================================================

    category_history = (
        monthly_category_revenue
        .groupby(
            "product_category_name"
        )["month"]
        .nunique()
        .reset_index(
            name="history_months"
        )
    )

    comparison = comparison.merge(
        category_history,
        on="product_category_name",
        how="left"
    )

    comparison["history_months"] = (
        pd.to_numeric(
            comparison["history_months"],
            errors="coerce"
        )
        .fillna(0)
        .astype(int)
    )

    # ============================================================
    # DATA QUALITY CLASSIFICATION
    # ============================================================

    def classify_category(row):

        previous_revenue = row[
            "previous_revenue"
        ]

        latest_revenue = row[
            "latest_revenue"
        ]

        previous_orders = row[
            "previous_orders"
        ]

        latest_orders = row[
            "latest_orders"
        ]

        history_months = row[
            "history_months"
        ]

        if (
            previous_revenue > 0
            and latest_revenue == 0
            and history_months >= 3
        ):
            return (
                "DISCONTINUITY — "
                "VALIDATE BEFORE ATTRIBUTING"
            )

        if (
            previous_revenue == 0
            and latest_revenue > 0
        ):
            return "NEW / REACTIVATED CATEGORY"

        if (
            previous_orders <= 2
            or latest_orders <= 2
        ):
            return "LOW VOLUME"

        return "COMPARABLE"

    comparison["evidence_status"] = (
        comparison.apply(
            classify_category,
            axis=1
        )
    )

    # ============================================================
    # CONTRIBUTION TO OBSERVED CATEGORY DECLINE
    # ============================================================

    declining = comparison[
        comparison["revenue_change"] < 0
    ].copy()

    total_decline = (
        declining["revenue_change"]
        .abs()
        .sum()
    )

    if total_decline > 0:

        comparison[
            "decline_contribution"
        ] = (
            comparison["revenue_change"]
            .clip(upper=0)
            .abs()
            .div(total_decline)
            * 100
        )

    else:

        comparison[
            "decline_contribution"
        ] = 0.0

    # ============================================================
    # DECLINE RANK
    # ============================================================

    declining = (
        comparison[
            comparison["revenue_change"] < 0
        ]
        .sort_values(
            "revenue_change",
            ascending=True
        )
        .reset_index(drop=True)
    )

    if not declining.empty:

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

    else:

        comparison["decline_rank"] = pd.NA

    # ============================================================
    # CUSTOMER REVIEW ANALYSIS
    # ============================================================

    review_data = reviews.merge(
        orders[
            [
                "order_id",
                "month"
            ]
        ],
        on="order_id",
        how="inner"
    )

    review_data["review_score"] = pd.to_numeric(
        review_data["review_score"],
        errors="coerce"
    )

    negative_reviews = review_data[
        review_data["review_score"] <= 2
    ].copy()

    if "review_comment_message" in negative_reviews.columns:

        negative_reviews = negative_reviews[
            negative_reviews[
                "review_comment_message"
            ].notna()
        ].copy()

        negative_reviews["text"] = (
            negative_reviews[
                "review_comment_message"
            ]
            .astype(str)
            .str.lower()
        )

    else:

        negative_reviews["text"] = ""

    # ============================================================
    # REVIEW THEMES
    # ============================================================

    theme_keywords = {

        "Delivery issues": [
            "entrega",
            "entregue",
            "chegou",
            "prazo",
            "atrasado",
            "atraso",
            "demorou",
            "delivery",
            "late"
        ],

        "Product issues": [
            "produto",
            "qualidade",
            "defeito",
            "quebrado",
            "errado",
            "product",
            "quality",
            "broken",
            "defective"
        ],

        "Order issues": [
            "pedido",
            "comprei",
            "recebi",
            "faltou",
            "cancelado",
            "order",
            "cancelled",
            "missing"
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

    # ============================================================
    # FINAL CLEANUP
    # ============================================================

    comparison["decline_rank"] = pd.to_numeric(
        comparison["decline_rank"],
        errors="coerce"
    )

    comparison["percentage_change"] = pd.to_numeric(
        comparison["percentage_change"],
        errors="coerce"
    )

    comparison["decline_contribution"] = pd.to_numeric(
        comparison["decline_contribution"],
        errors="coerce"
    ).fillna(0)

    comparison = comparison.sort_values(
        "revenue_change",
        ascending=True
    ).reset_index(drop=True)

    return (
        comparison,
        latest_month,
        previous_month,
        theme_counts
    )