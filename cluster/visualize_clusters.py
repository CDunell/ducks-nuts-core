
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.decomposition import PCA

def visualize_clusters(db_path: str):
    con = duckdb.connect(db_path)

    # Detect if pattern_cluster exists
    table_cols = [row[0] for row in con.execute("PRAGMA table_info('feature_snapshots')").fetchall()]
    if "pattern_cluster" in table_cols:
        df = con.execute("SELECT * FROM feature_snapshots WHERE pattern_cluster IS NOT NULL").fetchdf()
    else:
        df = con.execute("SELECT * FROM feature_snapshots").fetchdf()
        df["pattern_cluster"] = -1  # dummy cluster for visualization

    print("Data shape:", df.shape)
    print(df.head())

    if df.empty:
        print("No data to visualize")
        return

    features = df.select_dtypes(include="number").drop(columns=["pattern_cluster", "id"], errors="ignore").fillna(0)
    proj = PCA(n_components=2).fit_transform(features)

    outdir = Path(__file__).resolve().parent.parent / "output"
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / "umap_clusters.png"

    plt.figure(figsize=(8,6))
    scatter = plt.scatter(proj[:,0], proj[:,1], c=df["pattern_cluster"], cmap="tab10", alpha=0.7)
    plt.colorbar(scatter, label="Cluster")
    plt.title("Cluster Visualization (PCA)")
    plt.savefig(outpath)
    print("Cluster visualization saved to", outpath)

if __name__ == "__main__":
    import sys
    visualize_clusters(sys.argv[1])
