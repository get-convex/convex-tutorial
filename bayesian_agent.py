# bayesian_agent.py
import numpy as np
import random
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional
import math

class BayesianAgent:
    def __init__(self, num_states: int, num_actions: int, gamma: float = 0.99, 
                 exploration: float = 0.1, use_belief_update: bool = True):
        """
        Bayesian agent for Exploding Kittens.
        
        Args:
            num_states: Number of possible states (for Q-table compatibility)
            num_actions: Number of possible actions
            gamma: Discount factor
            exploration: Exploration rate for epsilon-greedy
            use_belief_update: Whether to use Bayesian belief updates
        """
        self.num_states = num_states
        self.num_actions = num_actions
        self.gamma = gamma
        self.exploration = exploration
        self.use_belief_update = use_belief_update
        
        # Q-table for action values
        self.Q = np.zeros((num_states, num_actions))
        
        # Prior knowledge about deck composition
        self.deck_composition_prior = self._initialize_deck_prior()
        
        # Belief state: probability distribution over game aspects
        self.beliefs = {
            'bomb_probability': 0.15,  # Prior belief about drawing a bomb
            'defuse_probability': 0.1,  # Prior belief about drawing a defuse
            'action_card_probs': {  # Prior probabilities for each action card
                'Skip': 0.15,
                'Attack': 0.15,
                'Shuffle': 0.1,
                'Nope': 0.1,
                'SeeFuture': 0.1,
                'Cat': 0.15
            }
        }
        
        # History of observed cards for Bayesian updates
        self.observed_cards = []
        self.known_cards_in_deck = []  # Cards we know are in deck (from SeeFuture)
        self.deck_size_history = []
        
        # Transition counts for Bayesian MDP model
        self.transition_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.reward_counts = defaultdict(lambda: defaultdict(list))
        
        # Hyperparameters for Bayesian updates
        self.alpha_prior = 1.0  # Prior for Beta distribution (successes)
        self.beta_prior = 1.0   # Prior for Beta distribution (failures)
        
    def _initialize_deck_prior(self) -> Dict[str, float]:
        """Initialize prior distribution over deck composition."""
        # Based on typical Exploding Kittens deck
        return {
            'Bomb': 0.10,
            'Defuse': 0.15,
            'Skip': 0.15,
            'Attack': 0.15,
            'Shuffle': 0.10,
            'Nope': 0.10,
            'SeeFuture': 0.10,
            'Cat': 0.15
        }
    
    def update_beliefs_from_state(self, state_dict: Dict, action: int, 
                                  reward: float, next_state_dict: Dict):
        """
        Update Bayesian beliefs based on observed state transition.
        
        Args:
            state_dict: Current state observation
            action: Action taken
            reward: Reward received
            next_state_dict: Next state observation
        """
        if not self.use_belief_update:
            return
            
        # Extract relevant information from state
        deck_size = state_dict.get('deck_size', 40)
        hand_size = state_dict.get('hand_size', 0)
        defuse_count = state_dict.get('defuse', 0)
        
        # Track deck size changes
        self.deck_size_history.append(deck_size)
        
        # If we have SeeFuture information, update known cards
        if 'peek' in state_dict:
            peek_cards = state_dict['peek']
            if peek_cards:
                self.known_cards_in_deck.extend([c for c in peek_cards if c is not None])
                # Limit to reasonable size
                self.known_cards_in_deck = self.known_cards_in_deck[-20:]
        
        # Update bomb probability using Beta-Bernoulli Bayesian update
        # This is a simplified model - in reality, we'd track multiple bombs
        if reward < 0:  # Negative reward often indicates drawing a bomb
            self.beliefs['bomb_probability'] = self._bayesian_update(
                self.beliefs['bomb_probability'], 
                success=True,  # Observed a bomb
                total_obs=deck_size,
                alpha_prior=self.alpha_prior,
                beta_prior=self.beta_prior
            )
        
        # Update transition model using Bayesian approach
        state_id = self._state_to_id(state_dict)
        next_state_id = self._state_to_id(next_state_dict)
        
        # Update counts for Bayesian transition probabilities
        self.transition_counts[state_id][action][next_state_id] += 1
        
        # Update reward model
        self.reward_counts[state_id][action].append(reward)
        
        # Update deck composition beliefs based on observed cards
        self._update_deck_composition_beliefs(state_dict, next_state_dict)
    
    def _bayesian_update(self, current_prob: float, success: bool, 
                         total_obs: int, alpha_prior: float, beta_prior: float) -> float:
        """
        Perform a Bayesian update using Beta-Bernoulli model.
        
        Args:
            current_prob: Current probability estimate
            success: Whether the event occurred
            total_obs: Total number of observations (deck size)
            alpha_prior: Prior alpha parameter
            beta_prior: Prior beta parameter
            
        Returns:
            Updated probability
        """
        # Convert current probability to Beta parameters
        total_pseudo_obs = alpha_prior + beta_prior
        alpha = alpha_prior + current_prob * total_pseudo_obs
        beta = beta_prior + (1 - current_prob) * total_pseudo_obs
        
        # Update based on observation
        if success:
            alpha += 1
        else:
            beta += 1
        
        # Return new probability (posterior mean)
        return alpha / (alpha + beta)
    
    def _update_deck_composition_beliefs(self, state_dict: Dict, next_state_dict: Dict):
        """Update beliefs about deck composition based on state changes."""
        # This is a simplified implementation
        # In a full implementation, we would track:
        # 1. Cards drawn by all players
        # 2. Cards played
        # 3. Cards we've seen
        
        current_deck_size = state_dict.get('deck_size', 40)
        next_deck_size = next_state_dict.get('deck_size', 40)
        
        # If deck size decreased, someone drew a card
        if next_deck_size < current_deck_size:
            # We become slightly less confident about exact composition
            for card_type in self.deck_composition_prior:
                # Slight entropy increase (simplified)
                self.deck_composition_prior[card_type] *= 0.99
            # Renormalize
            total = sum(self.deck_composition_prior.values())
            if total > 0:
                for card_type in self.deck_composition_prior:
                    self.deck_composition_prior[card_type] /= total
    
    def _state_to_id(self, state_dict: Dict) -> int:
        """Convert state dictionary to integer ID."""
        # Simplified hashing - in practice, use a proper state encoder
        if not hasattr(self, '_state_hash_cache'):
            self._state_hash_cache = {}
        
        # Create a hashable representation
        state_tuple = (
            state_dict.get('hand_size', 0),
            state_dict.get('defuse', 0),
            state_dict.get('deck_size', 40),
            state_dict.get('alive_count', 5),
            hash(str(state_dict.get('alive_mask', ()))),
            hash(str(state_dict.get('top3', ())))
        )
        
        state_hash = hash(state_tuple) % self.num_states
        
        # Cache for consistency
        key = str(state_tuple)
        if key not in self._state_hash_cache:
            self._state_hash_cache[key] = state_hash
        
        return self._state_hash_cache[key]
    
    def calculate_action_values(self, state_dict: Dict) -> np.ndarray:
        """
        Calculate Bayesian expected values for each action.
        
        Args:
            state_dict: Current state observation
            
        Returns:
            Array of action values
        """
        state_id = self._state_to_id(state_dict)
        hand_size = state_dict.get('hand_size', 0)
        defuse_count = state_dict.get('defuse', 0)
        deck_size = state_dict.get('deck_size', 40)
        alive_count = state_dict.get('alive_count', 5)
        
        # Base Q-values
        q_values = np.copy(self.Q[state_id])
        
        if self.use_belief_update:
            # Bayesian adjustments based on current beliefs
            
            # 1. Adjust for bomb probability when drawing
            bomb_prob = self.beliefs['bomb_probability']
            if bomb_prob > 0:
                # Value of drawing decreases with higher bomb probability
                # but increases if we have defuses
                draw_penalty = bomb_prob * (1 - min(defuse_count / 3.0, 1.0))
                q_values[0] -= draw_penalty  # A_DRAW is action 0
            
            # 2. Adjust for strategic considerations
            # If we have many cards, playing actions might be better
            if hand_size > 5:
                # Encourage playing action cards
                for action in [1, 2, 3, 4, 5, 6]:  # Action play indices
                    q_values[action] += 0.1
            
            # 3. Defuse play is valuable when bomb probability is high
            if bomb_prob > 0.2 and defuse_count > 0:
                q_values[7] += bomb_prob * 0.5  # A_PLAY_DEFUSE
            
            # 4. Use transition model uncertainty
            for action in range(self.num_actions):
                if state_id in self.transition_counts and action in self.transition_counts[state_id]:
                    transitions = self.transition_counts[state_id][action]
                    total_transitions = sum(transitions.values())
                    
                    if total_transitions > 0:
                        # Calculate entropy of transition distribution
                        entropy = 0
                        for count in transitions.values():
                            prob = count / total_transitions
                            if prob > 0:
                                entropy -= prob * math.log(prob)
                        
                        # Prefer actions with lower entropy (more predictable outcomes)
                        # Scale by exploration parameter
                        exploration_bonus = self.exploration * (1.0 / (1.0 + entropy))
                        q_values[action] += exploration_bonus
        
        return q_values
    
    def select_action(self, state_dict: Dict) -> int:
        """
        Select action using Bayesian-informed epsilon-greedy policy.
        
        Args:
            state_dict: Current state observation
            
        Returns:
            Selected action
        """
        if random.random() < self.exploration:
            # Exploration: random action
            return random.randint(0, self.num_actions - 1)
        
        # Exploitation: choose best action according to Bayesian values
        action_values = self.calculate_action_values(state_dict)
        return np.argmax(action_values)
    
    def update_q_value(self, state_dict: Dict, action: int, reward: float, 
                       next_state_dict: Dict, alpha: float = 0.1):
        """
        Update Q-value using Bayesian TD learning.
        
        Args:
            state_dict: Current state
            action: Action taken
            reward: Reward received
            next_state_dict: Next state
            alpha: Learning rate
        """
        state_id = self._state_to_id(state_dict)
        next_state_id = self._state_to_id(next_state_dict)
        
        # Calculate Bayesian TD target
        next_action_values = self.calculate_action_values(next_state_dict)
        td_target = reward + self.gamma * np.max(next_action_values)
        
        # Update Q-value
        td_error = td_target - self.Q[state_id, action]
        self.Q[state_id, action] += alpha * td_error
    
    def train(self, env, episodes: int = 50000, alpha: float = 0.1):
        """
        Train the Bayesian agent.
        
        Args:
            env: Environment instance
            episodes: Number of training episodes
            alpha: Learning rate
        """
        for episode in range(episodes):
            # Reset environment and get initial state
            # Assuming env.reset() returns a state dictionary
            if hasattr(env, 'reset'):
                state_dict = env.reset()
            else:
                # Fallback for custom environments
                state_dict = {'hand_size': 7, 'defuse': 1, 'deck_size': 40, 
                             'alive_count': env.players if hasattr(env, 'players') else 5}
            
            done = False
            total_reward = 0
            
            while not done:
                # Select action
                action = self.select_action(state_dict)
                
                # Take action
                if hasattr(env, 'step'):
                    # Assuming env.step returns (next_state_dict, reward, done, info)
                    result = env.step(action)
                    if len(result) >= 3:
                        next_state_dict, reward, done = result[:3]
                    else:
                        # Handle different return formats
                        next_state_dict, reward, done = result[0], result[1], result[2]
                else:
                    # Mock transition for testing
                    next_state_dict = state_dict.copy()
                    next_state_dict['deck_size'] = max(0, state_dict.get('deck_size', 40) - 1)
                    reward = 0
                    done = random.random() < 0.01  # Small chance of episode ending
                
                # Update beliefs
                self.update_beliefs_from_state(state_dict, action, reward, next_state_dict)
                
                # Update Q-values
                self.update_q_value(state_dict, action, reward, next_state_dict, alpha)
                
                # Transition to next state
                state_dict = next_state_dict
                total_reward += reward
            
            # Decay exploration rate
            self.exploration *= 0.9995
            self.exploration = max(0.01, self.exploration)
            
            # Logging
            if episode % 1000 == 0:
                print(f"Episode {episode}, Total Reward: {total_reward:.2f}, "
                      f"Exploration: {self.exploration:.3f}, "
                      f"Bomb Prob Belief: {self.beliefs['bomb_probability']:.3f}")
    
    def extract_policy(self) -> np.ndarray:
        """
        Extract policy from learned Q-values and beliefs.
        
        Returns:
            Array of action indices for each state
        """
        policy = np.zeros(self.num_states, dtype=int)
        
        for state_id in range(self.num_states):
            # Create a mock state dictionary for the state ID
            # In practice, you'd need a way to map state_id back to state_dict
            mock_state = {
                'hand_size': (state_id % 10),
                'defuse': ((state_id // 10) % 5),
                'deck_size': 40 - (state_id % 20),
                'alive_count': min(5, 1 + (state_id % 5))
            }
            
            # Get Bayesian action values
            action_values = self.calculate_action_values(mock_state)
            policy[state_id] = np.argmax(action_values)
        
        return policy
    
    def save_policy(self, path: str):
        """
        Save the learned policy to a file.
        
        Args:
            path: File path to save policy
        """
        policy = self.extract_policy()
        with open(path, "w") as f:
            for a in policy:
                f.write(f"{a}\n")
        
        # Also save belief state
        belief_path = path.replace(".txt", "_beliefs.json")
        import json
        with open(belief_path, "w") as f:
            json.dump({
                'beliefs': self.beliefs,
                'deck_composition_prior': self.deck_composition_prior,
                'exploration': self.exploration
            }, f, indent=2)
    
    def load_beliefs(self, path: str):
        """
        Load belief state from file.
        
        Args:
            path: File path to load beliefs from
        """
        import json
        with open(path, "r") as f:
            data = json.load(f)
            self.beliefs = data.get('beliefs', self.beliefs)
            self.deck_composition_prior = data.get('deck_composition_prior', self.deck_composition_prior)
            self.exploration = data.get('exploration', self.exploration)


# Simple integration example with your existing code
class BayesianEkoeAgent:
    """Wrapper to integrate BayesianAgent with your existing framework."""
    
    def __init__(self, num_states: int, num_actions: int):
        self.bayesian_agent = BayesianAgent(num_states, num_actions)
        self.num_states = num_states
        self.num_actions = num_actions
    
    def train(self, env, episodes: int = 50000):
        """Train the Bayesian agent."""
        self.bayesian_agent.train(env, episodes)
    
    def select_action(self, state_dict: Dict) -> int:
        """Select action using Bayesian agent."""
        return self.bayesian_agent.select_action(state_dict)
    
    def save_policy(self, path: str):
        """Save policy."""
        self.bayesian_agent.save_policy(path)
    
    def extract_policy(self) -> np.ndarray:
        """Extract policy."""
        return self.bayesian_agent.extract_policy()