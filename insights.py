def generate_insights(df):
    insights = []

    total = df["amt"].sum()

    top = df.groupby("cat")["amt"].sum().sort_values(ascending=False).index[0]
    insights.append(f"Top spending category: {top}")

    micro = df[df["amt"] < 200]["amt"].sum()
    if micro > 5000:
        insights.append("High micro-spending detected")

    food = df[df["cat"]=="Food"]["amt"].sum()
    if food > 5000:
        insights.append("Food expenses are high")

    return insights