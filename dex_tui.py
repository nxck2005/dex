from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Input, Static
from backend import get_dex_entry

__version__ = "0.1.0"

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
    CSS_PATH = "dex.css"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Container(
            Input(placeholder="Enter name or ID"),
            DexEntryInfo(),
        )
        yield Footer()

    async def on_input_submitted(self, message: Input.Submitted):
        """Handle input submission."""
        entry_name = message.value
        dex_entry_info = self.query_one(DexEntryInfo)
        dex_entry_info.update("Loading...")
        data = await get_dex_entry(entry_name)
        dex_entry_info.update_info(data)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    app = DexTUI()
    app.theme = "gruvbox"
    app.run()