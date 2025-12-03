# api.py

from flask import Flask, request, jsonify
from simulator.game import SimpleGame
from utils.state_encoder import state_to_id
from agents.policy_loader import q_policy, mle_policy
import pickle  # or your preferred game state persistence

app = Flask(__name__)

# Helper: Load and save game state (adjust as needed)
def load_game(game_id):
    with open(f"games/{game_id}.pkl", "rb") as f:
        return pickle.load(f)

def save_game(game_id, game):
    with open(f"games/{game_id}.pkl", "wb") as f:
        pickle.dump(game, f)

@app.route('/api/games/aiMove', methods=['POST'])
def ai_move():
    data = request.json
    game_id = data['gameId']
    game = load_game(game_id)
    player_idx = game.current_player()
    player_type = game.players[player_idx].type  # Adjust if your player object is different

    state_dict = game.get_canonical_state(player_idx)
    state_id = state_to_id(state_dict, num_states=100000)

    if player_type == 'qlearning':
        action = int(q_policy[state_id])
    elif player_type == 'mle':
        action = int(mle_policy[state_id])
    elif player_type == 'random':
        import random
        action = random.randint(0, 7)
    else:
        import random
        action = random.randint(0, 7)

    reward, done, info = game.step(action)
    save_game(game_id, game)
    return jsonify({
        'gameState': game.to_dict(),  # Implement to_dict() in your game class
        'action': action,
        'done': done,
        'info': info
    })

@app.route('/api/games/endTurn', methods=['POST'])
def end_turn():
    data = request.json
    game_id = data['gameId']
    game = load_game(game_id)

    # Advance to next alive player
    prev_player = game.current_player()
    next_player = game._next_alive(prev_player)
    game.turn = next_player

    # Optionally, update round number or other state here

    save_game(game_id, game)
    return jsonify({
        'gameState': game.to_dict(),
        'currentPlayerIndex': game.turn
    })
