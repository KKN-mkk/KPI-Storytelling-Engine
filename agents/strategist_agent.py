def generate_strategy(
    signal,
    diagnosis,
    themes,
    latest_month,
    previous_month
):

    revenue_change = signal["latest_change"]
    signal_status = signal["signal"]

    declining = diagnosis[
        diagnosis["revenue_change"] < 0
    ].head(3)

    top_theme = (
        max(themes, key=themes.get)
        if themes
        else "No dominant theme"
    )

    top_theme_count = (
        themes[top_theme]
        if themes
        else 0
    )

    # ============================================================
    # ABSTAIN
    # ============================================================

    if signal_status == "INSUFFICIENT HISTORY":

        return {
            "recommendation": (
                "Do not make a corrective business decision yet. "
                "Request additional historical data before "
                "interpreting the KPI movement."
            ),
            "confidence": "LOW",
            "reason": (
                "There is insufficient historical evidence to "
                "establish whether the movement is unusual."
            ),
            "top_theme": top_theme,
            "top_theme_count": top_theme_count,
            "latest_month": latest_month,
            "previous_month": previous_month,
            "decision_status": "ABSTAIN"
        }

    # ============================================================
    # NORMAL VARIATION
    # ============================================================

    if signal_status == "NORMAL VARIATION":

        recommendation = (
            "Continue monitoring revenue and the leading "
            "declining categories. Do not commit significant "
            "resources to corrective action while the movement "
            "remains within historical variation."
        )

        reason = (
            "The latest movement is not statistically unusual "
            "relative to the historical baseline."
        )

        confidence = "HIGH"
        decision_status = "MONITOR"

    # ============================================================
    # SIGNIFICANT CHANGE
    # ============================================================

    else:

        if declining.empty:

            recommendation = (
                "Investigate the revenue movement across "
                "operational and commercial drivers before "
                "taking corrective action."
            )

            reason = (
                "Revenue movement is statistically unusual, "
                "but no single declining category explains "
                "the movement sufficiently."
            )

            confidence = "MEDIUM"
            decision_status = "INVESTIGATE"

        else:

            top_category = declining.iloc[0][
                "product_category_name"
            ]

            category_change = declining.iloc[0][
                "percentage_change"
            ]

            contribution = declining.iloc[0].get(
                "decline_contribution",
                0
            )

            recommendation = (
                f"Investigate {top_category} first. "
                f"Revenue declined by {category_change:.1f}% "
                f"and this category contributes approximately "
                f"{contribution:.1f}% of the observed category "
                "decline. Review operational and customer "
                "evidence before selecting a corrective lever."
            )

            reason = (
                "The KPI movement is statistically unusual and "
                "a specific category contributes materially to "
                "the decline. Customer-review themes provide "
                "supporting evidence, but do not establish causation."
            )

            confidence = "HIGH"
            decision_status = "INVESTIGATE"

    return {
        "recommendation": recommendation,
        "confidence": confidence,
        "reason": reason,
        "top_theme": top_theme,
        "top_theme_count": top_theme_count,
        "latest_month": latest_month,
        "previous_month": previous_month,
        "decision_status": decision_status
    }