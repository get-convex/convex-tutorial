# bayesian_env_adapter.py
from simulator.game import SimpleGame
import numpy as np

class BayesianEnvAdapter:
    """Adapter to make your SimpleGame compatible with the BayesianAgent."""
    
    def __init__(self, num_players=5, num_states=100000, num_actions=8):
        self.game = SimpleGame(players=num_players)
        self.num_players = num_players
        self.num_states = num_states
        self.num_actions = num_actions
        self.current_player = 0
        self.max_steps_per_game = 1000  # Safety limit
    
    def reset(self):
        """Reset the game and return state for the current player."""
        self.game.reset()
        self.current_player = self.game.current_player()
        self.steps = 0
        
        state_dict = self.game.get_canonical_state(self.current_player)
        return state_dict
    
    def step(self, action):
        """
        Execute action for current player.
        Returns: (next_state_dict, reward, done, info)
        """
        self.steps += 1
        
        # Get current state before action
        current_state_dict = self.game.get_canonical_state(self.current_player)
        
        # Execute the action
        reward, done, info = self.game.step(action)
        
        # Update current player based on game state
        self.current_player = self.game.current_player()
        
        # Get state for the new current player
        if self.game.is_alive[self.current_player]:
            next_state_dict = self.game.get_canonical_state(self.current_player)
        else:
            # Find next alive player
            next_player = self.game._next_alive(self.current_player)
            self.current_player = next_player
            if self.game.is_alive[next_player]:
                next_state_dict = self.game.get_canonical_state(next_player)
            else:
                # No alive players (shouldn't happen)
                next_state_dict = current_state_dict
        
        # Safety check: prevent infinite loops
        if self.steps >= self.max_steps_per_game:
            done = True
            info['truncated'] = True
            reward = -1  # Penalty for taking too long
        
        # Add player index to info
        info['player'] = self.current_player
        
        return next_state_dict, reward, done, info
    
    def get_state_id(self, state_dict):
        """Convert state dictionary to integer ID."""
        try:
            from utils.state_encoder import state_to_id
            return state_to_id(state_dict, num_states=self.num_states)
        except ImportError:
            # Fallback implementation
            return hash(str(sorted(state_dict.items()))) % self.num_states