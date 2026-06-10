import duckdb
import pandas as pd
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import PCA
import joblib
from .cluster_config import ClusterConfig

class ClusterEngine:
    def __init__(self, db_path: str, config: ClusterConfig = ClusterConfig()):
        self.db_path = db_path
        self.config = config
        self.model = MiniBatchKMeans(n_clusters=config.n_clusters, random_state=42)

    def extract_features(self) -> pd.DataFrame:
        con = duckdb.connect(self.db_path)
        df = con.execute("""
            SELECT * FROM feature_snapshots
            WHERE pattern_cluster IS NULL
        """).fetchdf()
        con.close()
        return df

    def reduce_dimensionality(self, features: pd.DataFrame) -> pd.DataFrame:
        pca = PCA(n_components=self.config.pca_components)
        return pca.fit_transform(features)

    def cluster(self, data: pd.DataFrame) -> np.ndarray:
        return self.model.fit_predict(data)

    def write_clusters(self, original: pd.DataFrame, labels: np.ndarray):
        con = duckdb.connect(self.db_path)
        original["pattern_cluster"] = labels
        for _, row in original.iterrows():
            con.execute("UPDATE feature_snapshots SET pattern_cluster = ? WHERE id = ?", (int(row["pattern_cluster"]), row["id"]))
        con.close()
        if self.config.save_model:
            joblib.dump(self.model, "cluster/pattern_model.pkl")

    def run(self):
        df = self.extract_features()
        if df.empty:
            print("✅ No new feature snapshots to cluster.")
            return
        feature_cols = [col for col in df.columns if col not in {"id", "pattern_cluster"}]
        features = df[feature_cols].fillna(0)
        reduced = self.reduce_dimensionality(features)
        labels = self.cluster(reduced)
        self.write_clusters(df, labels)
        print(f"✅ Clustered {len(df)} snapshots into {self.config.n_clusters} clusters.")