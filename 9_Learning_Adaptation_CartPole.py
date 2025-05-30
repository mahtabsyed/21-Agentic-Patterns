# 9 - Learning and Adaptation
##  Reinforcement Learning with CartPole
# - To give you a concrete idea of how an agent can "learn by doing," let's look at a classic example from reinforcement learning: teaching an agent to balance a pole on a cart. 
# - This is often done using the "CartPole-v1" environment from the Gym library. The agent learns through trial and error, receiving rewards for keeping the pole upright and penalties for letting it fall. Over many attempts, it figures out the optimal actions to take in different situations.



import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

# 1. Define the Environment
# We'll use the 'CartPole-v1' environment, a classic control problem.
# make_vec_env creates a vectorized environment, which can speed up training.
env = make_vec_env("CartPole-v1", n_envs=1)

# 2. Choose an RL Algorithm
# We'll use Proximal Policy Optimization (PPO), a popular and robust algorithm.
# policy: "MlpPolicy" means a multi-layer perceptron (neural network) policy.
# env: The environment to train on.
# verbose: 1 to print training progress.
model = PPO("MlpPolicy", env, verbose=1)

# 3. Train the Agent
# The agent learns by interacting with the environment for a specified number of timesteps.
# During training, the agent will receive rewards and update its policy.
print("Training the agent...")
model.learn(total_timesteps=10000)
print("Training complete!")

# 4. Evaluate the Trained Agent
# We'll create a new environment instance for evaluation to ensure fair assessment.
eval_env = gym.make(
    "CartPole-v1", render_mode="human"
)  # Added render_mode for visualization

print("\nEvaluating the trained agent...")
obs, info = eval_env.reset()
for i in range(1000):  # Run for a maximum of 1000 timesteps or until done
    action, _states = model.predict(
        obs, deterministic=True
    )  # deterministic=True for consistent actions
    obs, rewards, terminated, truncated, info = eval_env.step(action)
    eval_env.render()  # Visualize the agent's performance (optional)
    if terminated or truncated:
        obs, info = eval_env.reset()
        print(
            f"Episode finished after {i+1} timesteps."
        )  # In this simple example, one episode is enough
        break
eval_env.close()
print("Evaluation complete.")