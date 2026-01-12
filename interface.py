import time
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.console import Console
from rich.progress_bar import ProgressBar


class TUI:
    def __init__(self, monitor_instance):
        self.monitor = monitor_instance
        self.console = Console()

    def _get_resources_panel(self):
        cpu = self.monitor.get_cpu_usage()
        ram = self.monitor.get_ram_usage()
        disk = self.monitor.get_disk_usage()
        gpu = self.monitor.get_gpu_usage()
        procs = self.monitor.get_top_processes()

        # FETCH NAMES from data.py
        specs = self.monitor.specs

        # --- COLORS ---
        cpu_color = "red" if cpu > 80 else "green"
        ram_color = "red" if ram['percent'] > 85 else "cyan"
        disk_color = "magenta"

        # --- TABLE ---
        table = Table(box=None, expand=True)
        # Wider column (25) to fit "AMD Ryzen 7 6800HS"
        table.add_column("Hardware", style="bold white", width=25)
        table.add_column("Bar", justify="center", width=20)
        table.add_column("Value", justify="right")

        # CPU ROW (Shows Name)
        cpu_label = specs['cpu'][:25]  # Truncate if too long
        table.add_row(
            cpu_label,
            ProgressBar(total=100, completed=cpu, width=20, style=cpu_color),
            f"{cpu}%"
        )

        # RAM ROW (Shows Size)
        table.add_row(
            f"RAM ({specs['ram']})",
            ProgressBar(total=100, completed=ram['percent'], width=20, style=ram_color),
            f"{ram['percent']}%"
        )

        # DISK ROW
        table.add_row(
            "SSD (C:)",
            ProgressBar(total=100, completed=disk['percent'], width=20, style=disk_color),
            f"{disk['percent']}%"
        )

        # GPU ROW (Shows Name + Temp)
        if gpu:
            gpu_load = gpu['load']
            gpu_color = "red" if gpu_load > 80 else "green"

            # Clean up name: "NVIDIA GeForce RTX 3060" -> "RTX 3060"
            gpu_label = gpu['name'].replace("NVIDIA GeForce ", "")[:25]
            gpu_text = f"{gpu_load:.0f}% | {gpu['temp']}°C"

            table.add_row(
                gpu_label,
                ProgressBar(total=100, completed=gpu_load, width=20, style=gpu_color),
                gpu_text
            )
        else:
            # Fallback if GPU is sleeping
            gpu_label = specs['gpu'].replace("NVIDIA GeForce ", "")[:25]
            table.add_row(gpu_label, "", "[dim]Deep Sleep[/]")

        # Process Section
        table.add_section()
        table.add_row("[b u]Top Processes[/]", "", "")
        for name, mem in procs:
            table.add_row(f"[dim]{name}[/]", "", f"[yellow]{mem:.2f} GB[/]")

        return Panel(table, title="[bold red]System Vitals[/]", border_style="red")

    def _get_network_panel(self):
        net = self.monitor.get_network_speed()

        dl_speed = net['download']
        dl_color = "green" if dl_speed < 1000 else "bold red"

        table = Table(box=None, expand=True)
        table.add_column("Direction", style="bold white")
        table.add_column("Speed", justify="right")

        table.add_row(
            "Download [green]⬇[/]",
            f"[{dl_color}]{dl_speed:.1f} KB/s[/]"
        )
        table.add_row(
            "Upload   [blue]⬆[/]",
            f"[blue]{net['upload']:.1f} KB/s[/]"
        )

        table.add_section()
        table.add_row("[dim]Status[/]", "[dim]Online[/]")

        return Panel(table, title="[bold blue]Network Uplink[/]", border_style="blue")

    def generate_dashboard(self):
        layout = Layout()

        layout.split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )

        layout["left"].update(self._get_resources_panel())
        layout["right"].update(self._get_network_panel())

        return layout

    def run(self):
        with Live(self.generate_dashboard(), refresh_per_second=4, screen=True) as live:
            while True:
                time.sleep(0.25)
                live.update(self.generate_dashboard())