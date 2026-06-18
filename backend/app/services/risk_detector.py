import json
import logging
import os
from typing import List, Dict, Any

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import tensorflow as tf
import yaml

logger = logging.getLogger(__name__)


class RiskDetector:
    def __init__(
        self,
        rules_path="risk_rules.yaml",
        model_path="risk_model.keras",
        labels_path="risk_labels.json",
    ):
        self.rules = self._load_rules(rules_path)
        self.model = None
        self.labels = []
        
        if os.path.exists(model_path) and os.path.exists(labels_path):
            self.model = tf.keras.models.load_model(model_path, compile=False)
            with open(labels_path, "r", encoding="utf-8") as label_file:
                self.labels = json.load(label_file)
        else:
            logger.warning(
                "TensorFlow risk model is unavailable. Run train_risk_model.py "
                "to enable ML-based risk detection."
            )

    def _load_rules(self, path) -> Dict:
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
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
                        
            # 2. TensorFlow-based detection (if the model is loaded)
            if self.model is not None and self.labels:
                probabilities = self.model(
                    tf.constant([chunk["text"]]),
                    training=False,
                )[0]
                prediction = self.labels[int(tf.argmax(probabilities).numpy())]
                if prediction != "Low Risk":
                    detected_risks.append({
                        "risk_type": "ml_detected_risk",
                        "severity": "high" if "High" in prediction else "medium",
                        "page": chunk["page"],
                        "source": chunk["source"],
                        "text": chunk["text"],
                        "method": "tensorflow"
                    })
                    
        return detected_risks
