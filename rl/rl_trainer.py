# ============================================
# Patch Date: 2025-07-24T04:08:24.245675Z
# Task: Add RL training loop using RLAgent and replay memory
# Source: STRICT PATCH MODE, based on:
#   - rl_agent.py (just patched)
#   - rl_engine.py (file-KT6p9yXpdmxTUdseVHWmSE)
#   - rl_memory.py (file-9tDcfAWwBfarAMMtR1ssZn)
# ============================================

import json
from feature_factory.rl.rl_agent import RLAgent

def train_rl_agent(memory_path="data/rl_memory.jsonl", episodes=5):
    agent = RLAgent()

    with open(memory_path, "r") as f:
        memory = [json.loads(line) for line in f]

    for ep in range(episodes):
        print(f"🎯 Episode {ep+1}/{episodes}")
        for step in memory:
            state = step["state"]
            action = step["action"]
            reward = step["reward"]
            next_state = step["next_state"]
            done = step["done"]
            agent.update(state, action, reward, next_state, done)
        agent.decay_epsilon()

    agent.save()
    print("✅ RL training complete. Q-table saved to data/q_table.pkl")