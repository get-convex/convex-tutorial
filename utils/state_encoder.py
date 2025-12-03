# utils/state_encoder.py
# deterministic encoder from a small state dict -> integer id in 0..N-1

def state_to_id(state_dict, num_states=100000):
    """
    Convert canonical state dict (from SimpleGame.get_canonical_state) into a hashed integer id.
    num_states controls size of state space (bigger -> fewer collisions).
    """
    # Build canonical tuple
    tpl = (
        int(state_dict.get("player", 0)),
        int(state_dict.get("hand_size", 0)),
        int(state_dict.get("defuse", 0)),
        int(state_dict.get("deck_size", 0)),
        int(state_dict.get("alive_count", 0)),
        tuple(state_dict.get("alive_mask", ())),
        tuple(state_dict.get("top3", ()))
    )
    # Use Python's built-in hash and map to positive
    h = hash(tpl) & 0x7FFFFFFF
    return h % num_states
