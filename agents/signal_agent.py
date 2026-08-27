import pandas as pd


def detect_signal(monthly_revenue):

    data = monthly_revenue.copy()

    # Make sure month is a datetime period
    data["month"] = pd.PeriodIndex(data["month"], freq="M")

    # Remove incomplete final month
    latest_month = data["month"].max()
    complete_data = data[data["month"] < latest_month].copy()

    # Calculate month-to-month percentage change
    complete_data["percentage_change"] = (
        complete_data["price"].pct_change() * 100
    )

    # Remove the first month because it has no previous month
    changes = complete_data["percentage_change"].dropna()

    # Latest complete month's change
    latest_change = changes.iloc[-1]

    # Use previous 12 months as historical baseline
    historical_changes = changes.iloc[-13:-1]

    historical_mean = historical_changes.mean()
    historical_std = historical_changes.std()

    # Calculate z-score
    if historical_std == 0 or pd.isna(historical_std):
        z_score = 0
    else:
        z_score = (
            latest_change - historical_mean
        ) / historical_std

    # Signal decision
    if abs(z_score) >= 2:
        signal = "SIGNIFICANT CHANGE"
    else:
        signal = "NORMAL VARIATION"

    return {
        "latest_month": str(complete_data["month"].iloc[-1]),
        "latest_change": latest_change,
        "historical_mean": historical_mean,
        "historical_std": historical_std,
        "z_score": z_score,
        "signal": signal
    }