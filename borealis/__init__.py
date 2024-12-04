"""
Main space for all things Project Borealis Related
"""

from borealis.pathfinder import pathfinder
from borealis.structure import setup_folders
from borealis.borealiscli import Clock
from borealis.borealiscli import PrettyCLI
from borealis.weather import download_weather
from borealis.aqi import aqi
from borealis.board import create_board
from borealis.evaluate import evaluate

__all__ = [
    "pathfinder",
    "setup_folders",
    "Clock",
    "PrettyCLI",
    "download_weather",
    "aqi",
    "create_board",
    "evaluate"
]