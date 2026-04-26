def detect_alerts(df):
    alerts = []

    # Micro spend alert
    micro = df[df["amt"] < 200]["amt"].sum()
    if micro > 5000:
        alerts.append("⚠️ High micro-spending detected")

    # Food overspend
    food = df[df["cat"]=="Food"]["amt"].sum()
    if food > 6000:
        alerts.append("🍔 Food spending too high")

    # Sudden spike detection
    daily = df.groupby("date")["amt"].sum()
    if daily.max() > daily.mean() * 2:
        alerts.append("🚨 Sudden spending spike detected")

    return alerts