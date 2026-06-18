import hashlib
import re
from typing import Iterable

import numpy as np


FEATURE_DIM = 512
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def _feature_index(token: str) -> int:
    digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "little") % FEATURE_DIM


def text_to_features(text: str) -> np.ndarray:
    tokens = TOKEN_PATTERN.findall(text.lower())
    features = np.zeros(FEATURE_DIM, dtype=np.float32)

    for token in tokens:
        features[_feature_index(f"word:{token}")] += 1.0

    for left, right in zip(tokens, tokens[1:]):
        features[_feature_index(f"bigram:{left}_{right}")] += 1.0

    norm = np.linalg.norm(features)
    if norm:
        features /= norm

    return features


def texts_to_features(texts: Iterable[str]) -> np.ndarray:
    rows = [text_to_features(text) for text in texts]
    if not rows:
        return np.empty((0, FEATURE_DIM), dtype=np.float32)
    return np.stack(rows).astype(np.float32)
