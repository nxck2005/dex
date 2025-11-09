import os
from textual_serve.server import Server
import tomllib

def main() -> None:
    """Run the application."""
    
    # Read version from pyproject.toml
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
        version = data["project"]["version"]

    app_command = f"python -m src.dex_tui"
    app_title = f"DexTUI v{version}"

    # Use textual-serve for web deployment
    port = int(os.environ.get("PORT", 8080))
    server = Server(command=app_command, port=port, title=app_title)
    server.serve()

if __name__ == "__main__":
    main()