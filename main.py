import os
from textual_serve import Server
from src.dex_tui import DexTUI
import tomllib

def main() -> None:
    """Run the application."""
    
    # Read version from pyproject.toml
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
        version = data["project"]["version"]

    app = DexTUI()
    app.theme = "gruvbox"
    app.title = f"DexTUI v{version}"

    # Use textual-serve for web deployment
    port = int(os.environ.get("PORT", 8080))
    server = Server(app, port=port)
    server.run()

if __name__ == "__main__":
    main()