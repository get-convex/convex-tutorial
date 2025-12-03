# trainers/train_mle.py
"""
Train an MLE-based policy using simulated transitions.
Either:
 - run simulations inside this script (calls simulator.generate_transitions.run_games_and_write)
 - OR load an existing CSV of transitions.

Usage:
python -m trainers.train_mle --simulate --games 2000 --out transitions_medium.csv
python -m trainers.train_mle --in transitions_medium.csv --num_states 100000 --num_actions 8 --gamma 0.95 --out policy_mle.txt
"""
import argparse
import numpy as np
import pandas as pd
from collections import defaultdict
from utils.state_encoder import state_to_id
import os

def solve_policy_from_df(df, num_states, num_actions, gamma):
    # Counting transitions and rewards
    N = {}
    R_sum = {}
    R_count = {}

    for _, row in df.iterrows():
        s = int(row['s'])
        a = int(row['a'])
        r = float(row['r'])
        sp = int(row['sp'])
        if s not in N:
            N[s] = {}
        if a not in N[s]:
            N[s][a] = {}
        if sp not in N[s][a]:
            N[s][a][sp] = 0
        N[s][a][sp] += 1

        if s not in R_sum:
            R_sum[s] = {}
            R_count[s] = {}
        if a not in R_sum[s]:
            R_sum[s][a] = 0.0
            R_count[s][a] = 0
        R_sum[s][a] += r
        R_count[s][a] += 1

    # Estimate T and R
    T = {}
    R = np.zeros((num_states, num_actions))
    for s in N:
        for a in N[s]:
            total = sum(N[s][a].values())
            T[(s, a)] = {sp: count/total for sp, count in N[s][a].items()}
            R[s, a] = R_sum[s][a] / R_count[s][a]

    # Value iteration
    V = np.zeros(num_states)
    max_iters = 5000
    for it in range(max_iters):
        V_next = np.zeros_like(V)
        for s in range(num_states):
            action_values = []
            for a in range(num_actions):
                if (s, a) in T:
                    expected_future = 0.0
                    for sp, prob in T[(s, a)].items():
                        expected_future += prob * V[sp]
                    Q = R[s, a] + gamma * expected_future
                else:
                    Q = R[s, a]
                action_values.append(Q)
            V_next[s] = max(action_values) if action_values else 0
        diff = np.max(np.abs(V_next - V))
        V = V_next
        if diff < 1e-6:
            print("Converged after", it+1, "iterations")
            break

    # Extract policy
    policy = np.zeros(num_states, dtype=np.int32)
    for s in range(num_states):
        action_values = []
        for a in range(num_actions):
            if (s, a) in T:
                expected_future = 0.0
                for sp, prob in T[(s, a)].items():
                    expected_future += prob * V[sp]
                Q = R[s, a] + gamma * expected_future
            else:
                Q = R[s, a]
            action_values.append(Q)
        policy[s] = int(np.argmax(action_values))
    return policy

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="infile", type=str, help="Input CSV with transitions")
    parser.add_argument("--simulate", action='store_true', help="Run simulations and produce local CSV before training")
    parser.add_argument("--games", type=int, default=2000)
    parser.add_argument("--players", type=int, default=5)
    parser.add_argument("--out", type=str, default="transitions_medium.csv")
    parser.add_argument("--num_states", type=int, default=100000)
    parser.add_argument("--num_actions", type=int, default=8)
    parser.add_argument("--gamma", type=float, default=0.95)
    parser.add_argument("--policy_out", type=str, default="policy_mle.txt")
    args = parser.parse_args()

    if args.simulate:
        # Lazy import to avoid circular imports
        from simulator.generate_transitions import run_games_and_write
        run_games_and_write(args.games, args.players, args.out, num_states=args.num_states)
        infile = args.out
    else:
        infile = args.infile

    if infile is None or not os.path.exists(infile):
        raise FileNotFoundError("No input CSV found; use --simulate or provide --in")

    df = pd.read_csv(infile)
    policy = solve_policy_from_df(df, num_states=args.num_states, num_actions=args.num_actions, gamma=args.gamma)

    # Write policy
    with open(args.policy_out, 'w') as f:
        for p in policy:
            f.write(f"{int(p)}\n")
    print("Wrote policy to", args.policy_out)

if __name__ == "__main__":
    main()
