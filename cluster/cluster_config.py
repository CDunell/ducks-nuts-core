from dataclasses import dataclass

@dataclass
class ClusterConfig:
    n_clusters: int = 10
    pca_components: int = 5
    save_model: bool = True