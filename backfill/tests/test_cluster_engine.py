from feature_factory.cluster.cluster_engine import ClusterEngine
from feature_factory.cluster.cluster_config import ClusterConfig
import os

def test_cluster_engine_runs(tmp_path):
    db_path = tmp_path / "test.duckdb"
    engine = ClusterEngine(str(db_path), config=ClusterConfig(n_clusters=2, pca_components=2))
    # create dummy table with required schema
    import duckdb
    con = duckdb.connect(str(db_path))
    con.execute("CREATE TABLE feature_snapshots (id INTEGER, f1 FLOAT, f2 FLOAT, pattern_cluster INTEGER);")
    con.execute("INSERT INTO feature_snapshots VALUES (1, 0.1, 0.2, NULL), (2, 0.2, 0.3, NULL);")
    con.close()
    engine.run()
    con = duckdb.connect(str(db_path))
    result = con.execute("SELECT COUNT(*) FROM feature_snapshots WHERE pattern_cluster IS NOT NULL;").fetchone()[0]
    assert result == 2