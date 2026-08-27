def generate_strategy(
    signal,
    diagnosis,
    themes,
    latest_month,
    previous_month
):

    # --------------------------------
    # SIGNAL
    # --------------------------------

    revenue_change = signal["latest_change"]
    signal_status = signal["signal"]

    # --------------------------------
    # TOP DECLINING CATEGORIES
    # --------------------------------

    declining = diagnosis[
        diagnosis["revenue_change"] < 0
    ].head(3)

    # --------------------------------
    # TOP REVIEW THEME
    # --------------------------------

    top_theme = max(
        themes,
        key=themes.get
    )

    top_theme_count = themes[top_theme]

    # --------------------------------
    # STRATEGY LOGIC
    # --------------------------------

    if signal_status == "NORMAL VARIATION":

        recommendation = (
            "Do not take a major corrective action yet. "
            "Continue monitoring revenue and the leading "
            "declining categories before committing resources."
        )

        confidence = "HIGH"

        reason = (
            "The overall revenue movement is within "
            "historical variation, so the evidence does "
            "not justify an aggressive intervention."
        )

    else:

        top_category = declining.iloc[0][
            "product_category_name"
        ]

        category_change = declining.iloc[0][
            "percentage_change"
        ]

        recommendation = (
            f"Investigate {top_category} first. "
            f"Revenue declined by {category_change:.1f}% "
            "in the latest period. Review product, order "
            "and delivery issues before deciding on a "
            "corrective action."
        )

        confidence = "MEDIUM"

        reason = (
            "The KPI movement appears unusual and a "
            "specific category is contributing materially "
            "to the decline, but review evidence alone "
            "does not establish causation."
        )

    # --------------------------------
    # RETURN STRATEGY
    # --------------------------------

    return {
        "recommendation": recommendation,
        "confidence": confidence,
        "reason": reason,
        "top_theme": top_theme,
        "top_theme_count": top_theme_count,
        "latest_month": latest_month,
        "previous_month": previous_month
    }