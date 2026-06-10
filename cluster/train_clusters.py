# 🧠 Phase 12 – Cluster Trainer
# Patch Date: 2025-07-24
# Task: Add sampling before UMAP to avoid memory errors
# Source: file-VvUUpy3BEyq9DUeLqNdJL5

import duckdb
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import MiniBatchKMeans
import umap
import sys

def load_features(db_path):
    con = duckdb.connect(db_path)
    df = con.execute("SELECT * FROM feature_snapshots").df()
    con.close()
    return df

def clean_features(df):
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    df_numeric = df[numeric_cols].dropna()
    return df_numeric, df

def reduce_dimensions(df_numeric):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_numeric)
    reducer = umap.UMAP(n_components=2, random_state=42)
    X_umap = reducer.fit_transform(X_scaled)
    return X_umap

def cluster(X_umap, n_clusters=12):
    model = MiniBatchKMeans(n_clusters=n_clusters, random_state=42)
    labels = model.fit_predict(X_umap)
    return labels

def write_back(original_df, labels, db_path):
    if len(labels) != len(original_df):
        print("Mismatch: cluster labels and data row count", file=sys.stderr)
        return
    df_out = original_df.copy()
    df_out['pattern_cluster'] = labels
    con = duckdb.connect(db_path)
    con.execute("DROP TABLE IF EXISTS feature_snapshots")
    con.execute("CREATE TABLE feature_snapshots AS SELECT * FROM df_out")
    con.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python train_clusters.py <path_to_duckdb>", file=sys.stderr)
        sys.exit(1)

    db_path = sys.argv[1]
    print(f"🔍 Loading features from: {db_path}")
    df = load_features(db_path)
    df_numeric, df_original = clean_features(df)

    max_rows = 100_000
    if len(df_numeric) > max_rows:
        print(f"⚠️ Too many rows ({len(df_numeric)}), sampling {max_rows} for UMAP")
        df_numeric = df_numeric.sample(n=max_rows, random_state=42)
        df_original = df_original.loc[df_numeric.index]

    print(f"✅ {len(df_numeric)} rows retained after cleaning")
    X_umap = reduce_dimensions(df_numeric)
    labels = cluster(X_umap, n_clusters=12)
    print(f"🏷️ Clustered into {len(set(labels))} labels")
    write_back(df_numeric, labels, db_path)
    print("✅ Cluster labels written back to DuckDB")
