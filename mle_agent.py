# mle_agent.py
import numpy as np
from collections import defaultdict
from simulator.env import EkoeEnvironment

class MLEAgent:
    def __init__(self, num_states, num_actions, gamma=0.99):
        self.num_states = num_states
        self.num_actions = num_actions
        self.gamma = gamma

        # MLE counts
        self.N = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.Rsum = defaultdict(lambda: defaultdict(float))
        self.Rcount = defaultdict(lambda: defaultdict(int))

        self.T = {}   # transition probabilities
        self.R = np.zeros((num_states, num_actions))

    def collect_data(self, env: EkoeEnvironment, episodes=20000):
        """Run the simulator to collect (s,a,r,sp) transitions."""
        for _ in range(episodes):
            s = env.reset()
            done = False

            while not done:
                a = np.random.randint(self.num_actions)     # random exploration
                sp, r, done = env.step(a)

                # Record counts
                self.N[s][a][sp] += 1
                self.Rsum[s][a] += r
                self.Rcount[s][a] += 1

                s = sp

    def estimate_mdp(self):
        """Convert counts → T and R"""
        for s in self.N:
            for a in self.N[s]:
                total = sum(self.N[s][a].values())
                self.T[(s, a)] = {
                    sp: count / total for sp, count in self.N[s][a].items()
                }
                self.R[s, a] = self.Rsum[s][a] / self.Rcount[s][a]

    def value_iteration(self, tol=1e-6):
        V = np.zeros(self.num_states)

        while True:
            Vn = np.copy(V)
            for s in range(self.num_states):
                qs = []
                for a in range(self.num_actions):
                    if (s, a) in self.T:
                        exp_future = sum(prob * V[sp] for sp, prob in self.T[(s, a)].items())
                        qs.append(self.R[s, a] + self.gamma * exp_future)
                Vn[s] = max(qs) if qs else 0

            if np.max(np.abs(Vn - V)) < tol:
                break
            V = Vn

        # Save policy
        self.V = V

    def extract_policy(self):
        policy = np.zeros(self.num_states, dtype=int)
        for s in range(self.num_states):
            qs = []
            for a in range(self.num_actions):
                if (s, a) in self.T:
                    q = self.R[s, a] + self.gamma * sum(
                        prob * self.V[sp] for sp, prob in self.T[(s, a)].items()
                    )
                else:
                    q = self.R[s, a]
                qs.append(q)
            policy[s] = np.argmax(qs)
        return policy

    def save_policy(self, path):
        policy = self.extract_policy()
        with open(path, "w") as f:
            for a in policy:
                f.write(f"{a}\n")
