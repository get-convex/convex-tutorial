# trainers/train_qlearning.py
"""
Train a Q-learning agent by running simulations (online).
Saves resulting policy file.

Usage:
python -m trainers.train_qlearning --episodes 5000 --players 5 --policy_out q_policy.txt
"""
import argparse
import numpy as np
import random
from simulator.game import SimpleGame, A_DRAW, ACTION_NAMES
from utils.state_encoder import state_to_id
import os

def greedy_action(Q, s, epsilon, num_actions):
    if random.random() < epsilon:
        return random.randrange(num_actions)
    return int(np.argmax(Q[s]))

def run_q_learning(episodes=2000, players=5, num_states=100000, num_actions=8,
                   alpha=0.1, gamma=0.95, epsilon_start=0.3, epsilon_final=0.05):
    Q = np.zeros((num_states, num_actions))
    epsilon = epsilon_start
    eps_decay = (epsilon_start - epsilon_final) / max(1, episodes)
    for ep in range(episodes):
        game = SimpleGame(players=players, rng=random.Random())
        game.reset()
        done = False
        steps = 0
        while not done and steps < 2000:
            p = game.current_player()
            if not game.is_alive[p]:
                game.turn = game._next_alive(p)
                continue
            s_dict = game.get_canonical_state(p)
            s = state_to_id(s_dict, num_states=num_states)
            # Choose action for this agent as learning agent if p == 0 (we pick player 0 to train)
            # For other players use baseline policy
            if p == 0:
                a = greedy_action(Q, s, epsilon, num_actions)
            else:
                # baseline: prefer skip if available, else draw
                if 'Skip' in game.hands[p]:
                    a = 1
                else:
                    a = A_DRAW

            r, done, info = game.step(a)
            sp_dict = game.get_canonical_state(p)
            sp = state_to_id(sp_dict, num_states=num_states)

            # Q update for p==0 only (we train the first agent)
            if p == 0:
                # Note: If next state terminal, target = r
                if done:
                    target = r
                else:
                    target = r + gamma * np.max(Q[sp])
                Q[s, a] += alpha * (target - Q[s, a])

            steps += 1

        # decay epsilon
        epsilon = max(epsilon_final, epsilon - eps_decay)

    policy = np.argmax(Q, axis=1)
    return policy

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=2000)
    parser.add_argument("--players", type=int, default=5)
    parser.add_argument("--num_states", type=int, default=100000)
    parser.add_argument("--num_actions", type=int, default=8)
    parser.add_argument("--alpha", type=float, default=0.1)
    parser.add_argument("--gamma", type=float, default=0.95)
    parser.add_argument("--epsilon_start", type=float, default=0.3)
    parser.add_argument("--epsilon_final", type=float, default=0.05)
    parser.add_argument("--policy_out", type=str, default="policy_q.txt")
    args = parser.parse_args()

    policy = run_q_learning(episodes=args.episodes,
                            players=args.players,
                            num_states=args.num_states,
                            num_actions=args.num_actions,
                            alpha=args.alpha,
                            gamma=args.gamma,
                            epsilon_start=args.epsilon_start,
                            epsilon_final=args.epsilon_final)
    with open(args.policy_out, 'w') as f:
        for p in policy:
            f.write(f"{int(p)}\n")
    print("Wrote Q policy to", args.policy_out)

if __name__ == "__main__":
    main()
