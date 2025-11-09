import os
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Header, Footer, DataTable, Static, Input
from textual.worker import Worker
from .backend import get_dex_entry, get_all_pokemon

__version__ = "1.0.0"
_current_dir = os.path.dirname(os.path.abspath(__file__))

class DexEntryInfo(Static):

    def update_info(self, data: dict):
        if "error" in data:
            self.update(data["error"])
            return

        height_m = data.get('height', 0) / 10.0
        weight_kg = data.get('weight', 0) / 10.0

        info = (
            f"[bold]{data.get('name', 'Unknown')} (#{data.get('id', 'N/A')})[/bold]\n\n"
            f"Types: {', '.join(data.get('types', []))}\n"
            f"Abilities: {', '.join(data.get('abilities', []))}\n"
            f"Height: {height_m:.1f} m\n"
            f"Weight: {weight_kg:.1f} kg\n\n"
            "[bold]Stats:[/bold]\n"
        )
        stats = data.get("stats", {})
        for stat, value in stats.items():
            info += f"- {stat.replace('_', '-').capitalize()}: {value}\n"
        
        if data.get("flavor_text"):
            info += f"\n[bold]Dex Entry:[/bold]\n{data['flavor_text']}\n"

        self.update(info)


class DexTUI(App):
    TITLE = f"dex v{__version__}"
    CSS_PATH = os.path.join(_current_dir, "static", "dex.css")
    BINDINGS = [
        ("enter", "select_pokemon", "Select Pokémon"),
    ]

    def __init__(self):
        super().__init__()
        self.all_pokemon = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Search for a Pokémon")
        yield Horizontal(
            DexEntryInfo(id="dex-entry"),
            DataTable(id="dex-table"),
        )
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("ID", "Name")
        self.run_worker(self.load_initial_data, exclusive=True, thread=True)

    def on_input_changed(self, message: Input.Changed) -> None:
        if not self.all_pokemon:
            return
        
        table = self.query_one(DataTable)
        search_term = message.value.lower()
        
        table.clear()
        for pokemon in self.all_pokemon:
            if search_term in pokemon["name"].lower() or search_term == str(pokemon["id"]):
                table.add_row(pokemon["id"], pokemon["name"].capitalize())

    def on_input_submitted(self, message: Input.Submitted) -> None:
        table = self.query_one(DataTable)
        if table.rows:
            table.move_cursor(row=0)
            self.action_select_pokemon()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.action_select_pokemon()

    def action_select_pokemon(self) -> None:
        table = self.query_one(DataTable)
        if not table.rows:
            return
            
        row_key = table.cursor_row
        row_data = table.get_row_at(row_key)
        if not row_data:
            return
            
        entry_id = row_data[0]
        
        dex_entry_info = self.query_one(DexEntryInfo)
        dex_entry_info.update("Loading...")
        self.run_worker(lambda: self.fetch_pokemon_data(entry_id), exclusive=True, thread=True)

    # --- Worker Methods ---

    def load_initial_data(self) -> None:
        """Worker to load all Pokémon names from the backend."""
        pokemon_list = get_all_pokemon()
        self.call_from_thread(self.update_pokemon_table, pokemon_list)

    def fetch_pokemon_data(self, pokemon_id: int) -> None:
        """Worker to fetch detailed data for a single Pokémon."""
        data = get_dex_entry(pokemon_id)
        self.call_from_thread(self.update_dex_entry, data)

    # --- UI Update Methods ---

    def update_pokemon_table(self, pokemon_list: list[dict]) -> None:
        """Called from worker to update the main data table."""
        self.all_pokemon = pokemon_list
        table = self.query_one(DataTable)
        for pokemon in self.all_pokemon:
            table.add_row(pokemon["id"], pokemon["name"].capitalize())

    def update_dex_entry(self, data: dict) -> None:
        """Called from worker to update the dex entry info panel."""
        dex_entry_info = self.query_one(DexEntryInfo)
        dex_entry_info.update_info(data)
