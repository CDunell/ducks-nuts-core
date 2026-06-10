# ============================================
# Patch Date: 2025-07-24T04:07:11.320239Z
# Task: Add Q-learning RL agent
# Source: STRICT PATCH MODE, based on:
#   - rl_config.py (file-QcYja9stLdsVUoE2Lw61X8)
#   - rl_engine.py (file-KT6p9yXpdmxTUdseVHWmSE)
#   - rl_memory.py (file-9tDcfAWwBfarAMMtR1ssZn)
# ============================================

import random
import pickle
from collections import defaultdict
from .rl_config import RLConfig

class RLAgent:
    def __init__(self, config: RLConfig = RLConfig()):
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.config = config
        self.epsilon = config.epsilon_start

    def get_action(self, state: dict) -> str:
        state_key = self._serialize_state(state)
        if random.random() < self.epsilon:
            return self._random_action()
        return max(self.q_table[state_key], key=self.q_table[state_key].get, default=self._random_action())

    def update(self, state, action, reward, next_state, done):
        state_key = self._serialize_state(state)
        next_key = self._serialize_state(next_state)
        current_q = self.q_table[state_key][action]
        max_future_q = max(self.q_table[next_key].values(), default=0.0)
        target = reward + (self.config.gamma * max_future_q * (0 if done else 1))
        self.q_table[state_key][action] = current_q + 0.1 * (target - current_q)  # α = 0.1

    def decay_epsilon(self):
        self.epsilon = max(self.config.epsilon_end, self.epsilon * self.config.epsilon_decay)

    def _serialize_state(self, state: dict) -> str:
        return str(sorted(state.items()))

    def _random_action(self) -> str:
        return "default_strategy"  # fallback or inject real action space

    def save(self, path="data/q_table.pkl"):
        with open(path, "wb") as f:
            pickle.dump(dict(self.q_table), f)

    def load(self, path="data/q_table.pkl"):
        with open(path, "rb") as f:
            raw = pickle.load(f)
            self.q_table = defaultdict(lambda: defaultdict(float), raw)