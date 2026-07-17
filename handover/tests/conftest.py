"""Put handover/scripts on sys.path so tests can import registry.py directly.

The scripts are standalone hook entry points, not an installed package.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
