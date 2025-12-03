# q_agent.py
import numpy as np
import random
from simulator.env import EkoeEnvironment   # your simulator environment

class QLearningAgent:
    def __init__(self, num_states, num_actions, gamma=0.99, alpha=0.1, epsilon=0.1):
        self.num_states = num_states
        self.num_actions = num_actions
        self.gamma = gamma
        self.alpha = alpha
        self.epsilon = epsilon

        # Initialize Q-table
        self.Q = np.zeros((num_states, num_actions))

    def select_action(self, state):
        # epsilon-greedy
        if random.random() < self.epsilon:
            return random.randint(0, self.num_actions - 1)
        return np.argmax(self.Q[state])

    def train(self, env: EkoeEnvironment, episodes=50000):
        for ep in range(episodes):
            s = env.reset()
            done = False

            while not done:
                a = self.select_action(s)
                sp, r, done = env.step(a)

                # Q update
                target = r + self.gamma * np.max(self.Q[sp])
                self.Q[s, a] += self.alpha * (target - self.Q[s, a])

                s = sp

    def extract_policy(self):
        return np.argmax(self.Q, axis=1)

    def save_policy(self, path):
        policy = self.extract_policy()
        with open(path, "w") as f:
            for a in policy:
                f.write(f"{a}\n")
