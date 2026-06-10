import click
from feature_factory.realtime.clusterer import run_clustering

@click.command(name="clusterer")
@click.option(
    "--input-db",
    default="features.duckdb",
    show_default=True,
    help="Path to the features database.",
)
@click.option(
    "--output",
    default="clusters.csv",
    show_default=True,
    help="Path to write the clusters CSV.",
)
@click.option(
    "--method",
    default="hdbscan",
    show_default=True,
    help="Clustering method to use.",
)
def clusterer(input_db: str, output: str, method: str):
    """
    Run feature clustering on the given database.
    """
    run_clustering(input_db=input_db, output=output, method=method)

if __name__ == "__main__":
    clusterer()
