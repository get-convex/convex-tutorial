# agents/policy_loader.py

import numpy as np

def load_policy(path):
    with open(path) as f:
        return np.array([int(line.strip()) for line in f])

# Load policies at module import (adjust paths as needed)
Q_POLICY_PATH = "medium.policy"
MLE_POLICY_PATH = "mle_policy.txt"

try:
    q_policy = load_policy(Q_POLICY_PATH)
except Exception as e:
    print(f"Could not load Q policy: {e}")
    q_policy = None

try:
    mle_policy = load_policy(MLE_POLICY_PATH)
except Exception as e:
    print(f"Could not load MLE policy: {e}")
    mle_policy = None
