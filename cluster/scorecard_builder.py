# ============================================
# Patch Date: 2025-07-24T08:30:00Z
# Task: Inject __main__ entrypoint for CLI execution
# Source: file-HJcSVGhRQ5AKNsb7Yp1HSQ
# STRICT PATCH MODE
# ============================================
import duckdb
import pandas as pd
from pathlib import Path

def build_scorecard(db_path: str, trade_log_path: str):
    df = pd.read_json(trade_log_path, lines=True)

    print("📈 Trade log shape:", df.shape)
    print(df.head())

    if df.empty:
        print("⚠️ No trades to score")
        return

    df["cluster"] = df["state"].apply(lambda s: s.get("pattern_cluster", -1))
    scorecard = df.groupby(["cluster", "strategy"])["reward"].agg(["mean", "count"]).reset_index()
    scorecard.columns = ["pattern_cluster", "strategy", "avg_reward", "sample_count"]

    outdir = Path(__file__).resolve().parent.parent / "output"
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / "ev_scorecard.csv"

    scorecard.to_csv(outpath, index=False)
    print("✅ Scorecard saved to", outpath)

if __name__ == "__main__":
    import sys
    build_scorecard(sys.argv[1], sys.argv[2])
