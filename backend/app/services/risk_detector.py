import yaml
import os
import pickle
from typing import List, Dict, Any

class RiskDetector:
    def __init__(self, rules_path="risk_rules.yaml", model_path="risk_model.pkl", vectorizer_path="risk_vectorizer.pkl"):
        self.rules = self._load_rules(rules_path)
        self.model = None
        self.vectorizer = None
        
        # Try loading ML model if it exists
        if os.path.exists(model_path) and os.path.exists(vectorizer_path):
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)
            with open(vectorizer_path, "rb") as f:
                self.vectorizer = pickle.load(f)

    def _load_rules(self, path) -> Dict:
        if not os.path.exists(path):
            return {}
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def detect_risks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Runs both rule-based and ML-based detection on chunks.
        """
        detected_risks = []
        
        for chunk in chunks:
            text = chunk["text"].lower()
            
            # 1. Rule-based detection
            for risk_type, rule_data in self.rules.items():
                for keyword in rule_data["keywords"]:
                    if keyword.lower() in text:
                        detected_risks.append({
                            "risk_type": risk_type,
                            "severity": rule_data["severity"],
                            "page": chunk["page"],
                            "source": chunk["source"],
                            "text": chunk["text"],
                            "method": "rule-based"
                        })
                        break # Prevent multiple triggers for same rule on same chunk
                        
            # 2. ML-based detection (if model is loaded)
            if self.model and self.vectorizer:
                X = self.vectorizer.transform([chunk["text"]])
                prediction = self.model.predict(X)[0]
                if prediction != "Low Risk":
                    # Add ML risk if not low risk
                    detected_risks.append({
                        "risk_type": "ml_detected_risk",
                        "severity": "high" if "High" in prediction else "medium",
                        "page": chunk["page"],
                        "source": chunk["source"],
                        "text": chunk["text"],
                        "method": "ml-based"
                    })
                    
        return detected_risks
