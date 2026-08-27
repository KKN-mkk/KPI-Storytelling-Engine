import pandas as pd


def detect_signal(monthly_revenue):
    """
    Signal Agent

    Determines whether the latest COMPLETE monthly revenue movement
    is statistically unusual relative to historical month-over-month
    movements.

    All quantitative calculations are deterministic.
    """

    data = monthly_revenue.copy()

    # ------------------------------------------------------------
    # CLEAN DATA
    # ------------------------------------------------------------

    data["month"] = pd.PeriodIndex(
        data["month"],
        freq="M"
    )

    data["price"] = pd.to_numeric(
        data["price"],
        errors="coerce"
    ).fillna(0)

    data = (
        data.groupby("month", as_index=False)["price"]
        .sum()
        .sort_values("month")
        .reset_index(drop=True)
    )

    if len(data) < 3:
        return {
            "latest_month": "",
            "latest_change": 0.0,
            "historical_mean": 0.0,
            "historical_std": 0.0,
            "z_score": 0.0,
            "signal": "INSUFFICIENT HISTORY",
            "confidence": "LOW",
            "historical_periods": 0,
        }

    # ------------------------------------------------------------
    # COMPLETE-MONTH LOGIC
    #
    # The source dataset's final calendar month can be incomplete.
    # Therefore:
    #
    # 2018-09 = potentially incomplete
    # 2018-08 = latest complete month
    #
    # ------------------------------------------------------------

    latest_raw_month = data["month"].max()

    complete_data = data[
        data["month"] < latest_raw_month
    ].copy()

    if len(complete_data) < 3:
        return {
            "latest_month": (
                str(complete_data["month"].iloc[-1])
                if not complete_data.empty
                else ""
            ),
            "latest_change": 0.0,
            "historical_mean": 0.0,
            "historical_std": 0.0,
            "z_score": 0.0,
            "signal": "INSUFFICIENT HISTORY",
            "confidence": "LOW",
            "historical_periods": 0,
        }

    # ------------------------------------------------------------
    # MONTH-OVER-MONTH CHANGE
    # ------------------------------------------------------------

    complete_data["percentage_change"] = (
        complete_data["price"]
        .pct_change()
        * 100
    )

    changes = (
        complete_data["percentage_change"]
        .dropna()
    )

    if changes.empty:
        return {
            "latest_month": str(
                complete_data["month"].iloc[-1]
            ),
            "latest_change": 0.0,
            "historical_mean": 0.0,
            "historical_std": 0.0,
            "z_score": 0.0,
            "signal": "INSUFFICIENT HISTORY",
            "confidence": "LOW",
            "historical_periods": 0,
        }

    # Latest complete-month movement
    latest_change = float(changes.iloc[-1])

    # ------------------------------------------------------------
    # HISTORICAL BASELINE
    #
    # Exclude the latest observation from the baseline.
    # Use up to 12 previous observations.
    # ------------------------------------------------------------

    historical_changes = changes.iloc[-13:-1]

    historical_periods = len(historical_changes)

    if historical_periods == 0:
        historical_mean = 0.0
        historical_std = 0.0
        z_score = 0.0
    else:
        historical_mean = float(
            historical_changes.mean()
        )

        historical_std = float(
            historical_changes.std()
        )

        if (
            historical_std == 0
            or pd.isna(historical_std)
        ):
            z_score = 0.0
        else:
            z_score = float(
                (
                    latest_change
                    - historical_mean
                )
                / historical_std
            )

    # ------------------------------------------------------------
    # CLASSIFICATION
    # ------------------------------------------------------------

    if historical_periods < 6:

        signal = "INSUFFICIENT HISTORY"
        confidence = "LOW"

    elif abs(z_score) >= 2:

        signal = "SIGNIFICANT CHANGE"
        confidence = "HIGH"

    else:

        signal = "NORMAL VARIATION"
        confidence = "MEDIUM"

    return {
        "latest_month": str(
            complete_data["month"].iloc[-1]
        ),
        "latest_change": latest_change,
        "historical_mean": historical_mean,
        "historical_std": historical_std,
        "z_score": z_score,
        "signal": signal,
        "confidence": confidence,
        "historical_periods": historical_periods,
    }