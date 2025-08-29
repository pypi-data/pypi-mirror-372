from pathlib import Path

scriptDir = Path(__file__).parent

__version__ = scriptDir.joinpath("VERSION").read_text()

__all__ = ["__version__"]
