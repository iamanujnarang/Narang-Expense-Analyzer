import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

def predict_spending(data):
    # Expect: columns = month, category, amt
    data['month_num'] = pd.factorize(data['month'])[0]

    predictions = {}

    for cat in data['cat'].unique():
        df = data[data['cat'] == cat]

        if len(df) < 2:
            continue

        X = df[['month_num']]
        y = df['amt']

        model = LinearRegression()
        model.fit(X, y)

        next_month = [[df['month_num'].max() + 1]]
        pred = model.predict(next_month)[0]

        predictions[cat] = round(pred, 2)

    return predictions