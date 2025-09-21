import requests
import time
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich import box

# Define your services
services = {
    "team1": {"face": "32405"},
    "team2": {"face": "31526"},
}

console = Console()

def get_status():
    """Poll all services and return a dict of results."""
    status = {}
    for team, svcs in services.items():
        status[team] = {}
        for svc, port in svcs.items():
            try:
                r = requests.get(f"http://127.0.0.1:{port}/healthz", timeout=2)
                if "ok" in r.text.lower():
                    status[team][svc] = "[green]OK[/green]"
                else:
                    status[team][svc] = "[red]ERR[/red]"
            except Exception as e:
                print(2)
                status[team][svc] = "[red]ERR[/red]"
                print(e)
    return status

def render_table(status):
    """Create a Rich table from the status dict."""
    table = Table(title="Uptime Dashboard", box=box.SIMPLE_HEAVY)
    table.add_column("Team", style="bold cyan")
    
    # Add service columns dynamically
    service_names = list(next(iter(services.values())).keys())
    for svc in service_names:
        table.add_column(svc.upper(), justify="center")
    
    # Fill rows with statuses
    for team, svcs in status.items():
        row = [team] + [svcs[svc] for svc in service_names]
        table.add_row(*row)
    return table

with Live(refresh_per_second=2, console=console, screen=False) as live:
    while True:
        status = get_status()
        live.update(render_table(status))
        time.sleep(5)  # update interval
