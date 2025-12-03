# simulator/generate_transitions.py
"""
CLI to generate transitions by running simulated games.
Outputs CSV file with columns: s,a,r,sp
"""
import argparse
import csv
from collections import deque
from simulator.game import SimpleGame, ACTION_NAMES, A_DRAW
from utils.state_encoder import state_to_id
import random

def baseline_policy(game, player_index):
    """
    Simple baseline: if have defuse and deck top likely bomb? Randomly:
    - Prefer to play Skip if available (ends turn without drawing)
    - Else if have Defuse and hand_size small, keep it (no-op)
    - Else draw.
    Return action integer.
    """
    hand = game.hands[player_index]
    if 'Skip' in hand:
        return 1  # PLAY_SKIP
    if 'Attack' in hand and random.random() < 0.05:
        return 2  # PLAY_ATTACK occasionally
    # otherwise draw
    return A_DRAW

def run_games_and_write(num_games, players, out_csv, num_states=100000, seed=0):
    rng = random.Random(seed)
    fieldnames = ['s', 'a', 'r', 'sp']
    with open(out_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for g in range(num_games):
            game = SimpleGame(players=players, rng=rng)
            game.reset()
            done = False
            # Avoid infinite games; cap steps per game
            steps = 0
            max_steps = 1000
            while not done and steps < max_steps:
                p = game.current_player()
                # Skip dead players (shouldn't be necessary because SimpleGame.step advances)
                if not game.is_alive[p]:
                    game.turn = game._next_alive(p)
                    continue
                s_dict = game.get_canonical_state(p)
                s_id = state_to_id(s_dict, num_states=num_states)

                # Choose action: if p==0 (we can choose to record transitions only for one player),
                # but here we record transitions for all players (typical)
                if game.players <= 1:
                    action = A_DRAW
                else:
                    action = baseline_policy(game, p)

                # Execute and get reward/sp
                r, done, info = game.step(action)
                sp_dict = game.get_canonical_state(p if (not info.get('exploded', False)) else p)
                sp_id = state_to_id(sp_dict, num_states=num_states)

                writer.writerow({'s': s_id, 'a': action, 'r': r, 'sp': sp_id})
                steps += 1

            # end of game
    print(f"Wrote transitions to {out_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", type=int, default=1000, help="Number of simulated games")
    parser.add_argument("--players", type=int, default=5, help="Players per game")
    parser.add_argument("--out", type=str, default="transitions.csv", help="Output CSV file")
    parser.add_argument("--num_states", type=int, default=100000, help="Number of hashed states")
    parser.add_argument("--seed", type=int, default=0, help="RNG seed")
    args = parser.parse_args()
    run_games_and_write(args.games, args.players, args.out, num_states=args.num_states, seed=args.seed)
