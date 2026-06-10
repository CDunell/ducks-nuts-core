import click
from feature_factory.scorecard import generate_scorecard

@click.command()
@click.option(
    "--input-db",
    default="features.duckdb",
    show_default=True,
    help="Path to the features database.",
)
@click.option(
    "--report",
    default="scorecard.md",
    show_default=True,
    help="Path to write the Markdown scorecard report.",
)
def scorecard(input_db: str, report: str):
    """
    Generate a feature scorecard report from the given database.
    """
    generate_scorecard(input_db=input_db, report_path=report)

if __name__ == "__main__":
    scorecard()
