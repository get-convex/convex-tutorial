from flask import Flask, request, jsonify
from flask_cors import CORS
from simulator.game import SimpleGame

app = Flask(__name__)
CORS(app)

games = {}
game_counter = 1

@app.route('/api/create_game', methods=['POST'])
def create_game():
    global game_counter
    data = request.get_json()
    players = data.get('players', 2)
    if not isinstance(players, int) or players < 2:
        return jsonify({'error': 'Invalid number of players'}), 400
    game = SimpleGame(players=players)
    game_id = str(game_counter)
    games[game_id] = game
    game_counter += 1
    return jsonify({'game_id': game_id})

@app.route('/api/game_state/<game_id>', methods=['GET'])
def get_game_state(game_id):
    game = games.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    state = {
        'hands': game.hands,
        'defuse_counts': game.defuse_counts,
        'is_alive': game.is_alive,
        'discard': game.discard,
        'turn': game.turn,
        'attack_counter': game.attack_counter,
        'deck_size': len(game.deck),
        'players': game.players,
    }
    return jsonify(state)

@app.route('/api/play_card/<game_id>', methods=['POST'])
def play_card(game_id):
    game = games.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    data = request.get_json()
    action = data.get('action')
    reinsertion_position = data.get('reinsertion_position', None)
    if action is None or not isinstance(action, int):
        return jsonify({'error': 'Invalid action'}), 400
    try:
        reward, done, info = game.step(action, reinsertion_position=reinsertion_position)
        return jsonify({'reward': reward, 'done': done, 'info': info})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/draw_card/<game_id>', methods=['POST'])
def draw_card(game_id):
    game = games.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    try:
        reward, done, info = game.step(0)  # 0 = DRAW
        return jsonify({'reward': reward, 'done': done, 'info': info})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset/<game_id>', methods=['POST'])
def reset_game(game_id):
    game = games.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    game.reset()
    return jsonify({'status': 'Game reset'})

if __name__ == '__main__':
    app.run(debug=True)
