# 🔒 PATCHED: 2025-07-25
# Task: Re-add `run` command and ensure proper invocation via asyncio and guard
# Source file: src/feature_factory/backfill/cli.py (file-turn6file0)

# backfill/cli.py

import typer
import uuid
import asyncio
from datetime import datetime

from .storage import Storage
from .models import BackfillJob, BackfillStatus
from .core import BackfillEngine
from .monitor import get_job_progress, format_progress_report
from .recovery import reset_failed_chunks
from .chunker import generate_chunks
from .batch import backfill_top_symbols
from realtime.symbols import load as load_symbols, save as save_symbols, active as active_symbols

app = typer.Typer(help="Backfill CLI")
symbols_app = typer.Typer(help="Manage pinned symbols")
app.add_typer(symbols_app, name="symbols")


@symbols_app.command("list")
def symbols_list():
    """Show all symbols and their enabled/disabled status."""
    for entry in load_symbols():
        state = "enabled" if entry["enabled"] else "disabled"
        typer.echo(f"{entry['symbol']:12s}  {state}")


@symbols_app.command("add")
def symbols_add(symbol: str = typer.Argument(..., help="Symbol to add, e.g. HYPEUSDT")):
    """Add a new symbol (enabled by default)."""
    symbol = symbol.upper()
    data = load_symbols()
    if any(e["symbol"] == symbol for e in data):
        typer.echo(f"{symbol} already exists")
        raise typer.Exit(1)
    data.append({"symbol": symbol, "enabled": True})
    save_symbols(data)
    typer.echo(f"Added {symbol}")


@symbols_app.command("enable")
def symbols_enable(symbol: str = typer.Argument(...)):
    """Enable a disabled symbol."""
    symbol = symbol.upper()
    data = load_symbols()
    for entry in data:
        if entry["symbol"] == symbol:
            entry["enabled"] = True
            save_symbols(data)
            typer.echo(f"Enabled {symbol}")
            return
    typer.echo(f"{symbol} not found")
    raise typer.Exit(1)


@symbols_app.command("disable")
def symbols_disable(symbol: str = typer.Argument(...)):
    """Disable a symbol without removing it."""
    symbol = symbol.upper()
    data = load_symbols()
    for entry in data:
        if entry["symbol"] == symbol:
            entry["enabled"] = False
            save_symbols(data)
            typer.echo(f"Disabled {symbol}")
            return
    typer.echo(f"{symbol} not found")
    raise typer.Exit(1)


@symbols_app.command("remove")
def symbols_remove(
    symbol: str = typer.Argument(...),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Permanently remove a symbol."""
    symbol = symbol.upper()
    data = load_symbols()
    if not any(e["symbol"] == symbol for e in data):
        typer.echo(f"{symbol} not found")
        raise typer.Exit(1)
    if not yes:
        typer.confirm(f"Remove {symbol} permanently?", abort=True)
    data = [e for e in data if e["symbol"] != symbol]
    save_symbols(data)
    typer.echo(f"Removed {symbol}")

@app.command()
def start(
    exchange: str = typer.Option(..., "--exchange", help="Exchange name"),
    symbol: str = typer.Option(..., "--symbol", help="Trading symbol"),
    start: str = typer.Option(..., "--start", help="Start time in ISO format"),
    end: str = typer.Option(..., "--end", help="End time in ISO format"),
    db_path: str = typer.Option(None, "--db-path", help="Path to DuckDB file"),
    chunk_hours: int = typer.Option(6, "--chunk-hours", help="Chunk size in hours"),
):
    '''
    Create a new backfill job and generate chunks.
    Times in ISO format, e.g. 2025-01-01T00:00:00
    '''
    st = datetime.fromisoformat(start)
    et = datetime.fromisoformat(end)
    job_id = str(uuid.uuid4())
    job = BackfillJob(
        id=job_id,
        exchange=exchange,
        symbol=symbol,
        start_time=st,
        end_time=et,
        status=BackfillStatus.PENDING,
    )
    storage = Storage(db_path=db_path)
    storage.create_job(job)
    generate_chunks(storage, job_id, chunk_hours)
    typer.echo(f"Created job {job_id}")

@app.command()
def status(
    job_id: str = typer.Argument(..., help="ID of the job to query"),
    db_path: str = typer.Option(None, "--db-path", help="Path to DuckDB file"),
):
    '''
    Show status of an existing job, including chunk progress.
    '''
    # open read-only to avoid locking conflicts
    storage = Storage(db_path=db_path, read_only=True)
    try:
        job = storage.get_job_by_id(job_id)
    except KeyError:
        typer.echo(f"Job {job_id} not found")
        raise typer.Exit(code=1)
    typer.echo(f"Job {job_id}: {job.status}")
    progress = get_job_progress(storage, job_id)
    typer.echo(format_progress_report(progress))

# rest unchanged...

@app.command()
def bulk(
    limit: int = typer.Option(10, "--limit", help="Number of top symbols"),
    years: int = typer.Option(2, "--years", help="Years of history"),
    chunk_hours: int = typer.Option(6, "--chunk-hours", help="Chunk size in hours"),
    db_path: str = typer.Option(None, "--db-path", help="Path to DuckDB file"),
):
    """
    Backfill top Binance symbols by volume over the past N years.
    """
    asyncio.run(backfill_top_symbols(limit, years, chunk_hours, db_path))
    typer.echo("Bulk backfill complete.")

# ⚠️ PATCHED: 2025-07-23
# Task: Add `pause` and `cancel` CLI commands to manage live backfill jobs
# Source file ID: file-1thi3tE5jB63ik9pcUGWo9

@app.command()
def pause(
    job_id: str = typer.Argument(..., help="Job ID to pause"),
    db_path: str = typer.Option(None, "--db-path", help="Path to DuckDB file"),
):
    """
    Pause a job by resetting RUNNING chunks to PENDING.
    Safe for resuming later.
    """
    storage = Storage(db_path=db_path)
    updated = storage.conn.execute(
        "UPDATE chunks SET status = 'PENDING' WHERE job_id = ? AND status = 'RUNNING'",
        [job_id]
    ).rowcount
    typer.echo(f"✅ Reset {updated} RUNNING chunks to PENDING for job {job_id}")

@app.command()
def cancel(
    job_id: str = typer.Argument(..., help="Job ID to cancel"),
    db_path: str = typer.Option(None, "--db-path", help="Path to DuckDB file"),
):
    """
    Cancel a job by marking all remaining chunks as FAILED.
    Cannot be resumed without manual reset.
    """
    storage = Storage(db_path=db_path)
    chunks_failed = storage.conn.execute(
        "UPDATE chunks SET status = 'FAILED' WHERE job_id = ? AND status IN ('PENDING', 'RUNNING')",
        [job_id]
    ).rowcount
    storage.conn.execute("UPDATE jobs SET status = 'FAILED' WHERE id = ?", [job_id])
    typer.echo(f"🛑 Canceled job {job_id}. Marked {chunks_failed} chunks as FAILED.")


@app.command()
def run(
    job_id: str = typer.Argument(..., help="ID of the job to process"),
    db_path: str = typer.Option(None, "--db-path", help="Path to DuckDB file"),
):
    """
    Process all pending chunks for a given job.
    """
    engine = BackfillEngine(storage=Storage(db_path=db_path))
    asyncio.run(engine.run(job_id))
    typer.echo(f"✅ Finished processing job {job_id}")


if __name__ == "__main__":
    app()
