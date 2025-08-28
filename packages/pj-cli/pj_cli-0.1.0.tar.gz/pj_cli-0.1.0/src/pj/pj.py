import sys

from rich.console import Console

stdout_console = Console()


def prettify() -> None:
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            stdout_console.print(line, end="")
    except KeyboardInterrupt:
        raise SystemExit(1)
    finally:
        stdout_console.print("\n[green]Command finished.[/green]")
