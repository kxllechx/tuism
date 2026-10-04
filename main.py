import psutil
import time

from rich.console import Console # type: ignore
from rich.layout import Layout # type: ignore
from rich.panel import Panel # type: ignore
from rich.table import Table # type: ignore
from rich.live import Live # type: ignore

console = Console()

def generate_dashboard():
    # layout structure
    layout = Layout()
    layout.split(
        Layout(name = "header", size = 3),
        Layout(name = "body"), 
        Layout(name = "footer", size = 3))

    layout["body"].split_row(
        Layout(name = "left"), Layout(name = "right")
    )

    # header content
    layout["header"].update(
        Panel(
            "[bold italic green]TUISystemMonitor v1[/bold italic green]",
            subtitle = "[dim]ctrl+c to exit[/dim]",
            border_style = "green"
        )
    )

    # left panel: cpu and memoryusage
    cpu_pct = psutil.cpu_percent(interval = None)
    mem = psutil.virtual_memory()

    stats_table = Table.grid(expand=True)
    stats_table.add_column(style="bold green")
    stats_table.add_column(style = "white")

    stats_table.add_row("CPU USAGE:", f"{cpu_pct}%")
    stats_table.add_row("TOTAL MEM:", f"{mem.total / (1024**3):.2f}GB")
    stats_table.add_row("USED MEM:", f"{mem.percent}%")
    stats_table.add_row("AVAIL. MEM:", f"{100 - mem.percent}%")

    layout["left"].update(Panel(stats_table, title = "[yellow]HARDWARE METRICS[/yellow]", border_style = "yellow"))

    # right panel; top mem procs
    proc_table = Table(expand= True, show_header= True, header_style = "bold magenta")
    proc_table.add_column("PID", style="dim", width=6)
    proc_table.add_column("Name", overflow="ellipsis")
    proc_table.add_column("MEM %", justify= "right", width = 6)

    # get highest mem procs
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied,psutil.ZombieProcess):
             pass

    processes = sorted(processes, key=lambda p: p['memory_percent'] or 0, reverse= True)[:5]
    for p in processes:
        name = p['name'] or "Unknown"
        mem_pct = f"{p['memory_percent']:.1f}%" if p['memory_percent'] else "0.0%"
        proc_table.add_row(str(p['pid']), name, mem_pct)

    layout["right"].update(Panel(proc_table, title = "[magenta]Tope Procs[/magenta]", border_style="magenta"))

    # footer
    layout["footer"].update(Panel(
        f"[dim]SYSTEM STATUS: Operational | Time: {time.strftime('%H:%M:%S')}[/dim]", border_style = "blue"
    ))

    return layout

if __name__ == "__main__":
    try:
        psutil.cpu_percent(interval=None)
        #lve loop every second
        with Live(generate_dashboard(), refresh_per_second = 1, screen =True) as live:
            while True:
                time.sleep(1)
                live.update(generate_dashboard())
    except KeyboardInterrupt:
        console.print("[bold red]MONITOR CLOSED.[/bold red]")


