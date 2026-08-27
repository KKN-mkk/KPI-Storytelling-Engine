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
    ].copy()

    declining = declining.sort_values(
        "revenue_change",
        ascending=True
    )

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
    # INSUFFICIENT HISTORY
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
                "determine whether the latest movement is unusual."
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

        # Look for a meaningful category decline.
        meaningful_declines = declining[
            (
                declining["previous_revenue"] > 0
            )
            &
            (
                declining["latest_orders"]
                +
                declining["previous_orders"]
                >= 5
            )
        ]

        if meaningful_declines.empty:

            recommendation = (
                "Continue monitoring revenue and category "
                "movements. The latest KPI change is within "
                "historical variation, so no major corrective "
                "action is recommended at this stage."
            )

            reason = (
                "The latest revenue movement is not statistically "
                "unusual and no sufficiently strong category-level "
                "evidence supports immediate intervention."
            )

            decision_status = "MONITOR"

        else:

            top_category = meaningful_declines.iloc[0]

            category_name = top_category[
                "product_category_name"
            ]

            category_change = top_category[
                "percentage_change"
            ]

            evidence_status = top_category[
                "evidence_status"
            ]

            if evidence_status.startswith(
                "DISCONTINUITY"
            ):

                recommendation = (
                    f"Validate the {category_name} revenue "
                    "discontinuity before taking corrective "
                    "business action. Check inventory, catalog "
                    "availability and order records first."
                )

                reason = (
                    f"{category_name} shows a large category-level "
                    "movement, but the pattern may represent a "
                    "sales discontinuity or sparse observation "
                    "rather than a confirmed business cause."
                )

                decision_status = "VALIDATE"

            else:

                recommendation = (
                    f"Monitor {category_name} closely. Revenue "
                    f"changed by {category_change:.1f}%, but the "
                    "overall KPI movement remains within historical "
                    "variation. Validate operational evidence "
                    "before committing resources."
                )

                reason = (
                    "The latest KPI movement is not statistically "
                    "unusual, so category-level movements should "
                    "be treated as investigation signals rather "
                    "than confirmed causes."
                )

                decision_status = "MONITOR"

        return {
            "recommendation": recommendation,
            "confidence": "MEDIUM",
            "reason": reason,
            "top_theme": top_theme,
            "top_theme_count": top_theme_count,
            "latest_month": latest_month,
            "previous_month": previous_month,
            "decision_status": decision_status
        }

    # ============================================================
    # SIGNIFICANT CHANGE
    # ============================================================

    meaningful_declines = declining[
        declining["previous_revenue"] > 0
    ].copy()

    if meaningful_declines.empty:

        recommendation = (
            "Investigate the unusual revenue movement across "
            "commercial and operational drivers before taking "
            "corrective action."
        )

        reason = (
            "Revenue movement is statistically unusual, but "
            "category evidence does not identify a sufficiently "
            "reliable single driver."
        )

        confidence = "MEDIUM"
        decision_status = "INVESTIGATE"

    else:

        top_category = meaningful_declines.iloc[0]

        category_name = top_category[
            "product_category_name"
        ]

        category_change = top_category[
            "percentage_change"
        ]

        contribution = top_category.get(
            "decline_contribution",
            0
        )

        evidence_status = top_category[
            "evidence_status"
        ]

        if evidence_status.startswith(
            "DISCONTINUITY"
        ):

            recommendation = (
                f"Investigate the {category_name} revenue "
                "discontinuity first. Validate inventory, "
                "catalog availability and order records before "
                "attributing the unusual KPI movement to customer "
                "or product behavior."
            )

            reason = (
                "The overall KPI movement is statistically unusual, "
                "but the leading category exhibits a potential "
                "discontinuity. The evidence supports validation, "
                "not causal attribution."
            )

            confidence = "MEDIUM"
            decision_status = "VALIDATE"

        else:

            recommendation = (
                f"Investigate {category_name} first. Revenue "
                f"changed by {category_change:.1f}% and this "
                f"category represents approximately "
                f"{contribution:.1f}% of the observed category "
                "decline. Validate operational and customer "
                "evidence before selecting a corrective lever."
            )

            reason = (
                "The KPI movement is statistically unusual and "
                "a category-level driver is visible. Customer "
                "review themes may provide supporting evidence, "
                "but they do not establish causation."
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