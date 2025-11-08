import os
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Header, Footer, DataTable, Static, Input
from .backend import get_dex_entry, get_all_pokemon

__version__ = "0.1.0"
_current_dir = os.path.dirname(os.path.abspath(__file__))

class DexEntryInfo(Static):
    """A widget to display dex entry information."""

    def update_info(self, data: dict):
        """Update the displayed information."""
        if "error" in data:
            self.update(data["error"])
            return

        info = (
            f"[bold]{data['name']} (#{data['id']})[/bold]\n\n"
            f"Types: {', '.join(data['types'])}\n"
            f"Abilities: {', '.join(data['abilities'])}\n"
            f"Height: {data['height']}\n"
            f"Weight: {data['weight']}\n\n"
            "[bold]Stats:[/bold]\n"
        )
        for stat, value in data["stats"].items():
            info += f"- {stat.capitalize()}: {value}\n"
        
        if data.get("flavor_text"):
            info += f"\n[bold]Dex Entry:[/bold]\n{data['flavor_text']}\n"

        self.update(info)


class DexTUI(App):
    """A Textual Dex app."""

    TITLE = f"dex v{__version__}"
    CSS_PATH = os.path.join(_current_dir, "static", "dex.css")
    BINDINGS = [
        ("enter", "select_pokemon", "Select Pokémon"),
    ]

    def __init__(self):
        super().__init__()
        self.all_pokemon = []

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Input(placeholder="Search for a Pokémon")
        yield Horizontal(
            DexEntryInfo(id="dex-entry"),
            DataTable(id="dex-table"),
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Called when the app is mounted."""
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("ID", "Name")
        self.all_pokemon = await get_all_pokemon()
        for i, pokemon in enumerate(self.all_pokemon):
            table.add_row(i + 1, pokemon["name"].capitalize())

    async def on_input_changed(self, message: Input.Changed) -> None:
        """Handle input changes to filter the table."""
        table = self.query_one(DataTable)
        search_term = message.value.lower()
        table.clear()
        for i, pokemon in enumerate(self.all_pokemon):
            if search_term in pokemon["name"] or search_term == str(i + 1):
                table.add_row(i + 1, pokemon["name"].capitalize())

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """Handle input submission to select the top result."""
        table = self.query_one(DataTable)
        if table.rows:
            table.move_cursor(row=0)
            await self.action_select_pokemon()

    async def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle data table row selection."""
        await self.action_select_pokemon()

    async def action_select_pokemon(self) -> None:
        """Select a Pokémon from the table."""
        table = self.query_one(DataTable)
        if not table.rows:
            return
            
        row_key = table.cursor_row
        row = table.get_row_at(row_key)
        entry_name = row[1]
        
        dex_entry_info = self.query_one(DexEntryInfo)
        dex_entry_info.update("Loading...")
        data = await get_dex_entry(entry_name)
        dex_entry_info.update_info(data)