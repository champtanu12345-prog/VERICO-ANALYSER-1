import json
import os

import numpy as np
import tensorflow as tf

from app.services.text_features import FEATURE_DIM, texts_to_features


LABELS = ["High Risk", "Low Risk", "Medium Risk"]


def train_model():
    print("Training TensorFlow risk model...")
    tf.keras.utils.set_random_seed(42)

    samples = [
        ("we are not responsible for any damages or losses", "High Risk"),
        ("the contractor accepts unlimited liability for every claim", "High Risk"),
        ("there is no cap on liability under this agreement", "High Risk"),
        ("the vendor has no right to audit our records", "High Risk"),
        ("customer information may be sold to third parties", "High Risk"),
        ("we may share confidential data without prior consent", "High Risk"),
        ("the supplier indemnifies us against all damages", "High Risk"),
        ("all intellectual property belongs exclusively to the client", "High Risk"),
        ("payment obligations continue even after service failure", "High Risk"),
        ("the company may change all terms without notice", "High Risk"),
        ("the customer waives every legal remedy", "High Risk"),
        ("third parties receive unrestricted access to personal data", "High Risk"),
        ("this agreement automatically renews for another year", "Medium Risk"),
        ("either party may terminate this contract immediately", "Medium Risk"),
        ("prices may increase after the initial subscription term", "Medium Risk"),
        ("the service can be suspended with limited notice", "Medium Risk"),
        ("disputes must be resolved through binding arbitration", "Medium Risk"),
        ("the notice period for termination is thirty days", "Medium Risk"),
        ("late payments will incur a reasonable service charge", "Medium Risk"),
        ("the contract renews unless cancelled before expiry", "Medium Risk"),
        ("usage limits may be revised during the contract term", "Medium Risk"),
        ("the warranty period is limited to ninety days", "Medium Risk"),
        ("subcontractors may be used to provide some services", "Medium Risk"),
        ("data will be retained for a limited period after termination", "Medium Risk"),
        ("this is a standard mutual non-disclosure agreement", "Low Risk"),
        ("payment is due within thirty days of receiving an invoice", "Low Risk"),
        ("both parties agree to act in good faith", "Low Risk"),
        ("total liability is capped at the fees paid", "Low Risk"),
        ("either party may terminate with ninety days written notice", "Low Risk"),
        ("customer data remains confidential and will not be sold", "Low Risk"),
        ("records may be audited once per year with notice", "Low Risk"),
        ("personal information is encrypted and access controlled", "Low Risk"),
        ("the vendor will comply with applicable privacy laws", "Low Risk"),
        ("services include reasonable technical support", "Low Risk"),
        ("changes to this agreement require written consent", "Low Risk"),
        ("the parties retain ownership of their existing property", "Low Risk"),
    ]

    texts = [text for text, _ in samples]
    features_array = texts_to_features(texts)
    label_ids = np.asarray(
        [LABELS.index(label) for _, label in samples],
        dtype=np.int32,
    )

    feature_input = tf.keras.Input(
        shape=(FEATURE_DIM,),
        dtype=tf.float32,
        name="text_features",
    )
    features = tf.keras.layers.Dense(64, activation="relu")(feature_input)
    features = tf.keras.layers.Dense(32, activation="relu")(features)
    features = tf.keras.layers.Dropout(0.2)(features)
    output = tf.keras.layers.Dense(
        len(LABELS),
        activation="softmax",
        name="risk_probabilities",
    )(features)

    model = tf.keras.Model(
        feature_input,
        output,
        name="contract_risk_classifier",
    )
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.005),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.fit(
        features_array,
        label_ids,
        epochs=120,
        batch_size=8,
        verbose=0,
    )

    backend_dir = os.path.dirname(os.path.abspath(__file__))
    keras_model_path = os.path.join(backend_dir, "risk_model.keras")
    lite_model_path = os.path.join(backend_dir, "risk_model.tflite")
    labels_path = os.path.join(backend_dir, "risk_labels.json")

    model.save(keras_model_path)

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    lite_model = converter.convert()
    with open(lite_model_path, "wb") as model_file:
        model_file.write(lite_model)

    with open(labels_path, "w", encoding="utf-8") as label_file:
        json.dump(LABELS, label_file, indent=2)

    _, accuracy = model.evaluate(features_array, label_ids, verbose=0)
    print(f"Keras model saved to {keras_model_path}")
    print(f"LiteRT model saved to {lite_model_path}")
    print(f"Training accuracy: {accuracy:.2%}")

if __name__ == "__main__":
    train_model()
