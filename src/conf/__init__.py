import json
from pathlib import Path

from src import APP_HOME

config = json.load(Path(__file__).parent.joinpath('conf.json').open())
config['project']['secret'] = APP_HOME.joinpath('.secret').read_text().strip()
