import pyfiglet
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, Footer, Header, Static

from htop.htop import Htop


class HtopTUI(App[None]):
    BINDINGS = [
        Binding("p", "toggle_view('processes')", "Processes", show=True),
        Binding("r", "toggle_view('priorities')", "Priorities", show=True),
        Binding("h", "toggle_view('hup')", "Ignored hup", show=True),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, htop: Htop):
        super().__init__()
        self.htop = htop
        self.view_mode = "processes"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(pyfiglet.figlet_format("AMSA25-26"), id="ascii")
        yield DataTable(id="process_table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("PID", "Command", "Type", "Priority")
        self.update_table()
        self.set_interval(2, self.update_table)

    def update_table(self) -> None:
        if self.view_mode == "processes":
            processes = self.htop.get_processes()
        elif self.view_mode == "priorities":
            processes = self.htop.get_priorities()
        else:  # hup
            processes = self.htop.get_hup()

        table = self.query_one(DataTable)
        table.clear()

        for process in processes:
            priority = str(process.priority) if process.priority is not None else "N/A"
            table.add_row(
                str(process.pid), process.command, process.type.value, priority
            )

    def action_toggle_view(self, view: str) -> None:
        self.view_mode = view
        self.update_table()
