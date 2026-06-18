import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
import pickle
import os

def train_model():
    print("Training ML risk model...")
    # Sample training data for the sake of the requirement
    data = {
        "text": [
            "we are not responsible for any damages",
            "unlimited liability falls on the contractor",
            "this agreement will automatically renew for another term",
            "the vendor has no right to audit our records",
            "we can terminate this contract immediately",
            "this is a standard non-disclosure agreement",
            "payment is due within 30 days",
            "both parties agree to act in good faith",
            "the total liability is capped at $1000",
            "we reserve the right to sell customer data"
        ],
        "label": [
            "High Risk", "High Risk", "Medium Risk", "High Risk", "Medium Risk", 
            "Low Risk", "Low Risk", "Low Risk", "Low Risk", "High Risk"
        ]
    }
    
    df = pd.DataFrame(data)
    
    vectorizer = TfidfVectorizer()
    model = LogisticRegression()
    
    # Fit vectorizer and model
    X = vectorizer.fit_transform(df["text"])
    model.fit(X, df["label"])
    
    # Save artifacts
    with open("backend/risk_vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
        
    with open("backend/risk_model.pkl", "wb") as f:
        pickle.dump(model, f)
        
    print("Model trained and saved successfully.")

if __name__ == "__main__":
    # Ensure backend directory exists if running from root
    os.makedirs("backend", exist_ok=True)
    train_model()
