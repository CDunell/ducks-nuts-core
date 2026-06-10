# ============================================
# Patch Date: 2025-07-24T04:19:27.879384Z
# Task: Hardcode flush_to_disk() to write to src/feature_factory/data/
# Source: file-KT6p9yXpdmxTUdseVHWmSE
# STRICT PATCH MODE
# ============================================

import os
from .rl_memory import RLMemory

class RewardEngine:
    def __init__(self):
        self.memory = RLMemory()

    def compute_reward(self, trade: dict) -> float:
        if trade.get("exit_reason") == "TP":
            return 1.0
        elif trade.get("exit_reason") == "SL":
            return -1.0
        else:
            return 0.0  # timeout or neutral exit

    def log_episode(self, state, action, reward, next_state, done=True):
        self.memory.append(state, action, reward, next_state, done)

    def flush_to_disk(self, path=os.path.join(os.path.dirname(__file__), "../data/rl_memory.jsonl")):
        import json
        with open(path, "w") as f:
            for episode in self.memory.buffer:
                json.dump({
                    "state": episode[0],
                    "action": episode[1],
                    "reward": episode[2],
                    "next_state": episode[3],
                    "done": episode[4]
                }, f)
                f.write("\n")