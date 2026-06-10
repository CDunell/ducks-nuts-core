# ============================================
# Patch Date: 2025-07-24T05:31:14.894153Z
# Task: Replay prints now also written to logs/replay_debug.log
# Source: file-GXPiunK4yVgk4ExN1ui3Cg
# STRICT PATCH MODE
# ============================================
import json
import os
from feature_factory.rl.rl_engine import RewardEngine

def replay(file_path: str):
    os.makedirs("logs", exist_ok=True)
    log = open("logs/replay_debug.log", "w", encoding="utf-8")

    def logline(msg):
        print(msg)
        log.write(msg + "\n")

    logline("🟢 START REPLAY: " + file_path)
    engine = RewardEngine()
    count = 0
    with open(file_path, "r") as f:
        for line in f:
            logline("[READ LINE] " + line.strip())
            trade = json.loads(line)
            reward = engine.compute_reward(trade)
            state = trade.get("state", {})
            action = trade.get("strategy")
            next_state = trade.get("next_state", {})
            logline(f"[EPISODE {count}] action={action}, reward={reward}")
            engine.log_episode(state, action, reward, next_state)
            count += 1

    logline(f"[TOTAL EPISODES] {count}")
    engine.flush_to_disk()
    logline("✅ Replay complete. Memory written.")
    log.close()
# ============================================
# Patch Date: 2025-07-24T05:33:46.903212Z
# Task: Append __main__ block to trigger replay
# Source: file-UoKkM9EXrewrbmteos4og9
# STRICT PATCH MODE
# ============================================
if __name__ == "__main__":
    replay("src/feature_factory/data/trade_log.jsonl")
