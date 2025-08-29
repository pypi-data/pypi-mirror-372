import os
import json
from hestia_earth.orchestrator import run

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(CURRENT_DIR, 'config', 'Cycle')


def should_recalculate(product: dict):
    return f"{product.get('termType')}.json" in os.listdir(CONFIG_PATH)


def recalculate(cycle: dict, product: dict):
    with open(os.path.join(CONFIG_PATH, f"{product.get('termType')}.json")) as f:
        config = json.load(f)

    return run(cycle, config)
