from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from clarity_cli.defs import TableColumn

verbose = True  # or False, depending on your use case


class CliTable():
    def __init__(self, table_name, columns: list[TableColumn]):
        self.out = CliOutput()
        self.table = Table(title=table_name)
        self.columns = columns
        for column in columns:
            self.table.add_column(column.name, style=column.color.value)

    def add_data(self, data: list[dict[str, str]], headers_mapping: dict[str, str]):
        for row in data:
            self.table.add_row(
                *[f'{row.get(headers_mapping[col.header], "")}' for col in self.table.columns])

    def print_table(self):
        self.out.print(self.table)


class CliOutput():
    _instance = None
    console: Console = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CliOutput, cls).__new__(cls)
            cls._instance.verbose = False  # Default value
            cls._instance.console = Console()
        return cls._instance

    def setup_context(self, ctx):
        self.verbose = ctx.obj.get('VERBOSE')

    def ok(self, message=None):
        if message:
            self.print(f"[green]{message}[/green]")

    def error(self, message=None):
        if message:
            self.print(f"[red][bold]{message}[bold][/red]")

    def warning(self, message=None):
        if message:
            self.print(f"[yellow]{message}[/yellow]")

    def main_message(self, message):
        self.print(Panel.fit(message, style="blue"))

    def print(self, message):
        self.console.print(message)

    def vprint(self, message):
        if self.verbose:
            self.print(f"[dim]{message}[/dim]")

    @staticmethod
    def bold(message):
        return f"[bold]{message}[/bold]"

    def run_sync_function(self, message, function, **args):
        with self.console.status(f"[bold green]{message}\n"):
            return function(**args)
