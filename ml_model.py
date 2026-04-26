from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib

vectorizer = CountVectorizer()
model = MultinomialNB()

def train_model(df):
    X = vectorizer.fit_transform(df['desc'])
    y = df['cat']
    model.fit(X, y)
    joblib.dump((model, vectorizer), "model.pkl")

def predict_category(desc):
    try:
        model, vectorizer = joblib.load("model.pkl")
        X = vectorizer.transform([desc])
        return model.predict(X)[0]
    except:
        return "Misc"