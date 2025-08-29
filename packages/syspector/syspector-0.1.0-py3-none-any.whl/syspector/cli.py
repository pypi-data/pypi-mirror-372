"""CLI using Click to provide quick commands."""
from __future__ import annotations
import click
import json

from .core import SystemInspector


@click.group()
@click.option("--interval", default=1.0, show_default=True, type=float)
@click.pass_context
def main(ctx, interval):
    """syspector CLI: check `syspector --help` for commands."""
    ctx.ensure_object(dict)
    ctx.obj["inspector"] = SystemInspector(poll_interval=interval)


@main.command()
@click.pass_context
def snapshot(ctx):
    """Print a single snapshot as JSON."""
    inspector = ctx.obj["inspector"]
    print(json.dumps(inspector.simple_report(), indent=2))


@main.command()
@click.argument("seconds", type=int, default=10)
@click.pass_context
def monitor(ctx, seconds):
    """Run an intervaled monitor in the terminal for `seconds` seconds."""
    inspector = ctx.obj["inspector"]
    import time

    end = time.time() + seconds
    try:
        while time.time() < end:
            r = inspector.simple_report()
            print(f"[{r['time']}] CPU {r['cpu']['percent']}% MEM {r['memory']['percent']}%")
            time.sleep(inspector.poll_interval)
    except KeyboardInterrupt:
        print("monitor stopped")
