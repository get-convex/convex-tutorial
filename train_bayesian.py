# train_bayesian.py
import argparse
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import time

from bayesian_agent import BayesianAgent
from bayesian_env_adapter import BayesianEnvAdapter
from utils.state_encoder import state_to_id

def train_bayesian_agent(config):
    """Main training function for Bayesian agent."""
    
    # Initialize environment and agent
    env = BayesianEnvAdapter(
        num_players=config.players,
        num_states=config.num_states,
        num_actions=config.num_actions
    )
    
    agent = BayesianAgent(
        num_states=config.num_states,
        num_actions=config.num_actions,
        gamma=config.gamma,
        exploration=config.epsilon_start,
        use_belief_update=True
    )
    
    # Training metrics
    episode_rewards = []
    episode_lengths = []
    win_rates = []
    recent_rewards = deque(maxlen=100)
    recent_wins = deque(maxlen=100)
    
    print(f"Starting Bayesian Agent Training")
    print(f"Episodes: {config.episodes}, Players: {config.players}")
    print(f"Gamma: {config.gamma}, Epsilon: {config.epsilon_start} -> {config.epsilon_end}")
    
    start_time = time.time()
    
    for episode in range(config.episodes):
        # Reset environment
        state_dict = env.reset()
        agent.current_player = 0
        
        done = False
        total_reward = 0
        steps = 0
        won = False
        
        while not done and steps < config.max_steps:
            # Select action using Bayesian agent
            action = agent.select_action(state_dict)
            
            # Take action
            next_state_dict, reward, done, info = env.step(action)
            
            # Update agent's beliefs and Q-values
            agent.update_beliefs_from_state(state_dict, action, reward, next_state_dict)
            agent.update_q_value(state_dict, action, reward, next_state_dict, alpha=config.alpha)
            
            # Transition to next state
            state_dict = next_state_dict
            total_reward += reward
            steps += 1
            
            # Check if current player won
            if done and 'winner' in info and info['winner'] == agent.current_player:
                won = True
        
        # Episode complete
        episode_rewards.append(total_reward)
        episode_lengths.append(steps)
        recent_rewards.append(total_reward)
        recent_wins.append(1 if won else 0)
        
        # Decay exploration rate
        agent.exploration = max(
            config.epsilon_end,
            config.epsilon_start * (config.epsilon_decay ** episode)
        )
        
        # Logging
        if (episode + 1) % config.log_interval == 0:
            avg_reward = np.mean(recent_rewards)
            win_rate = np.mean(recent_wins) * 100
            win_rates.append(win_rate)
            
            print(f"Episode {episode + 1}/{config.episodes}")
            print(f"  Avg Reward (last 100): {avg_reward:.3f}")
            print(f"  Win Rate (last 100): {win_rate:.1f}%")
            print(f"  Exploration: {agent.exploration:.4f}")
            print(f"  Bomb Probability Belief: {agent.beliefs['bomb_probability']:.3f}")
            print(f"  Steps: {steps}")
            
            # Save checkpoint
            if (episode + 1) % config.save_interval == 0:
                checkpoint_path = f"{config.save_dir}/bayesian_checkpoint_ep{episode+1}.txt"
                agent.save_policy(checkpoint_path)
                print(f"  Checkpoint saved: {checkpoint_path}")
        
        # Early stopping if consistently winning
        if len(recent_wins) >= 100 and np.mean(recent_wins) > 0.95:
            print(f"Early stopping at episode {episode+1} (win rate > 95%)")
            break
    
    # Training complete
    total_time = time.time() - start_time
    print(f"\nTraining completed in {total_time:.2f} seconds")
    
    # Save final policy
    final_policy_path = f"{config.save_dir}/bayesian_final_policy.txt"
    agent.save_policy(final_policy_path)
    print(f"Final policy saved: {final_policy_path}")
    
    # Plot training results
    if config.plot_results:
        plot_training_results(episode_rewards, win_rates, config)
    
    return agent, episode_rewards, win_rates

def plot_training_results(episode_rewards, win_rates, config):
    """Plot training metrics."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Plot rewards
    ax1.plot(episode_rewards, alpha=0.6, label='Episode Reward')
    
    # Smooth rewards
    if len(episode_rewards) >= 100:
        smoothed_rewards = np.convolve(episode_rewards, np.ones(100)/100, mode='valid')
        ax1.plot(range(99, len(episode_rewards)), smoothed_rewards, 
                'r-', linewidth=2, label='Smoothed (100 eps)')
    
    ax1.set_xlabel('Episode')
    ax1.set_ylabel('Reward')
    ax1.set_title('Bayesian Agent Training - Rewards')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot win rates
    if win_rates:
        episodes = [(i+1) * config.log_interval for i in range(len(win_rates))]
        ax2.plot(episodes, win_rates, 'g-', linewidth=2, marker='o', markersize=4)
        ax2.set_xlabel('Episode')
        ax2.set_ylabel('Win Rate (%)')
        ax2.set_title('Win Rate (last 100 episodes)')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim([0, 105])
    
    plt.tight_layout()
    plt.savefig(f"{config.save_dir}/bayesian_training_plot.png", dpi=150)
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Train Bayesian Agent for Exploding Kittens")
    
    # Environment parameters
    parser.add_argument("--players", type=int, default=5, help="Number of players")
    parser.add_argument("--num_states", type=int, default=100000, help="Number of state IDs")
    parser.add_argument("--num_actions", type=int, default=8, help="Number of actions")
    
    # Training parameters
    parser.add_argument("--episodes", type=int, default=20000, help="Number of training episodes")
    parser.add_argument("--max_steps", type=int, default=1000, help="Maximum steps per episode")
    parser.add_argument("--gamma", type=float, default=0.99, help="Discount factor")
    parser.add_argument("--alpha", type=float, default=0.1, help="Learning rate")
    
    # Exploration parameters
    parser.add_argument("--epsilon_start", type=float, default=0.3, help="Starting exploration rate")
    parser.add_argument("--epsilon_end", type=float, default=0.01, help="Minimum exploration rate")
    parser.add_argument("--epsilon_decay", type=float, default=0.9995, help="Exploration decay rate")
    
    # Logging and saving
    parser.add_argument("--log_interval", type=int, default=500, help="Log every N episodes")
    parser.add_argument("--save_interval", type=int, default=5000, help="Save checkpoint every N episodes")
    parser.add_argument("--save_dir", type=str, default="policies", help="Directory to save policies")
    parser.add_argument("--plot_results", action="store_true", help="Plot training results")
    
    # Evaluation
    parser.add_argument("--eval_episodes", type=int, default=100, help="Episodes for final evaluation")
    
    args = parser.parse_args()
    
    # Create save directory if it doesn't exist
    import os
    os.makedirs(args.save_dir, exist_ok=True)
    
    # Train the agent
    agent, rewards, win_rates = train_bayesian_agent(args)
    
    # Evaluate the agent
    env = BayesianEnvAdapter(num_players=args.players)

if __name__ == "__main__":
    main()