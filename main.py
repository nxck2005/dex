from src.dex_tui import DexTUI

if __name__ == "__main__":
    app = DexTUI()
    """ default theme for now """
    app.theme = "gruvbox"
    app.run()