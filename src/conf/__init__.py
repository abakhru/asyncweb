import json
from pathlib import Path

config = json.load(Path(__file__).parent.joinpath('conf.json').open())
