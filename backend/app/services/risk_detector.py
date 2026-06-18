import json
import logging
import os
import threading
from typing import List, Dict, Any

import numpy as np
import yaml

from app.services.text_features import text_to_features

logger = logging.getLogger(__name__)


def _load_interpreter(model_path: str):
    try:
        from ai_edge_litert.interpreter import Interpreter
    except ImportError:
        os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
        import tensorflow as tf

        Interpreter = tf.lite.Interpreter

    return Interpreter(model_path=model_path)


class RiskDetector:
    def __init__(
        self,
        rules_path="risk_rules.yaml",
        model_path="risk_model.tflite",
        labels_path="risk_labels.json",
    ):
        self.rules = self._load_rules(rules_path)
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.labels = []
        self._interpreter_lock = threading.Lock()
        
        if os.path.exists(model_path) and os.path.exists(labels_path):
            self.interpreter = _load_interpreter(model_path)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()[0]
            self.output_details = self.interpreter.get_output_details()[0]
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
            if self.interpreter is not None and self.labels:
                features = text_to_features(chunk["text"]).reshape(1, -1)
                with self._interpreter_lock:
                    self.interpreter.set_tensor(
                        self.input_details["index"],
                        features.astype(np.float32),
                    )
                    self.interpreter.invoke()
                    probabilities = self.interpreter.get_tensor(
                        self.output_details["index"]
                    )[0]
                prediction = self.labels[int(np.argmax(probabilities))]
                if prediction != "Low Risk":
                    detected_risks.append({
                        "risk_type": "ml_detected_risk",
                        "severity": "high" if "High" in prediction else "medium",
                        "page": chunk["page"],
                        "source": chunk["source"],
                        "text": chunk["text"],
                        "method": "tensorflow-lite"
                    })
                    
        return detected_risks
