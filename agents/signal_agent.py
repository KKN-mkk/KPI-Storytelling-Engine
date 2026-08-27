import pandas as pd


def detect_signal(monthly_revenue):
    """
    Detects whether the latest completed-month revenue movement
    is statistically unusual relative to the historical baseline.

    Quantitative truth is deterministic:
    - monthly revenue
    - percentage change
    - historical mean/std
    - z-score
    """

    data = monthly_revenue.copy()

    data["month"] = pd.PeriodIndex(data["month"], freq="M")
    data = data.sort_values("month").reset_index(drop=True)

    # The final month is treated as potentially incomplete.
    latest_month = data["month"].max()
    complete_data = data[data["month"] < latest_month].copy()

    if len(complete_data) < 3:
        return {
            "latest_month": str(complete_data["month"].iloc[-1])
            if len(complete_data)
            else "",
            "latest_change": 0.0,
            "historical_mean": 0.0,
            "historical_std": 0.0,
            "z_score": 0.0,
            "signal": "INSUFFICIENT HISTORY",
            "confidence": "LOW",
            "historical_periods": len(complete_data),
        }

    complete_data["percentage_change"] = (
        complete_data["price"].pct_change() * 100
    )

    changes = complete_data["percentage_change"].dropna()

    if len(changes) == 0:
        return {
            "latest_month": str(complete_data["month"].iloc[-1]),
            "latest_change": 0.0,
            "historical_mean": 0.0,
            "historical_std": 0.0,
            "z_score": 0.0,
            "signal": "INSUFFICIENT HISTORY",
            "confidence": "LOW",
            "historical_periods": 0,
        }

    latest_change = float(changes.iloc[-1])

    # Use up to the previous 12 observations as baseline.
    historical_changes = changes.iloc[-13:-1]

    historical_mean = float(historical_changes.mean())
    historical_std = float(historical_changes.std())

    if historical_std == 0 or pd.isna(historical_std):
        z_score = 0.0
    else:
        z_score = float(
            (latest_change - historical_mean) / historical_std
        )

    if len(historical_changes) < 6:
        signal = "INSUFFICIENT HISTORY"
        confidence = "LOW"
    elif abs(z_score) >= 2:
        signal = "SIGNIFICANT CHANGE"
        confidence = "HIGH"
    else:
        signal = "NORMAL VARIATION"
        confidence = "MEDIUM"

    return {
        "latest_month": str(complete_data["month"].iloc[-1]),
        "latest_change": latest_change,
        "historical_mean": historical_mean,
        "historical_std": historical_std,
        "z_score": z_score,
        "signal": signal,
        "confidence": confidence,
        "historical_periods": len(historical_changes),
    }