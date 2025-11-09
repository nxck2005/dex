import os
from textual.app import App
from .screens import DexScreen, SetupScreen
from .database import DB_PATH

__version__ = "1.0.0"
_current_dir = os.path.dirname(os.path.abspath(__file__))

class DexTUI(App):
    """The main application class."""

    CSS_PATH = os.path.join(_current_dir, "static", "dex.css")
    
    SCREENS = {
        "dex": DexScreen,
    }

    def on_mount(self) -> None:
        """Called when the app is first mounted."""
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(
                f"Database not found at {DB_PATH}. "
                "Please run `uv run data_pipeline.py --yes` to create it."
            )
        self.push_screen("dex")


if __name__ == "__main__":
    app = DexTUI()
    app.run()
