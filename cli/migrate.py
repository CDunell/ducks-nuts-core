#!/usr/bin/env python3
"""
Migration CLI: apply DuckDB SQL migrations in order to any database file.
"""
import click
import duckdb
import glob
import os

@click.command()
@click.option(
    '--db-path', '-d',
    type=click.Path(dir_okay=False, writable=True),
    default='./data/features_sample.duckdb',
    help='Path to the DuckDB file to migrate.'
)
@click.option(
    '--migrations-dir', '-m',
    type=click.Path(exists=True, file_okay=False),
    default='./migrations',
    help='Directory containing numbered .sql migration files.'
)
def migrate(db_path, migrations_dir):
    """
    Apply all SQL files in migrations_dir (sorted by name) to db_path.
    """
    # ensure data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # connect (will create file if missing)
    conn = duckdb.connect(database=db_path)
    click.echo(f"Migrating database at {db_path}")

    # find SQL files
    files = sorted(glob.glob(os.path.join(migrations_dir, '*.sql')))
    if not files:
        click.echo('No migration files found.', err=True)
        conn.close()
        return

    for sql_file in files:
        click.echo(f"Applying {os.path.basename(sql_file)}...")
        with open(sql_file, 'r') as f:
            sql = f.read()
        conn.execute(sql)

    conn.close()
    click.echo('Migration complete.')

if __name__ == '__main__':
    migrate()
