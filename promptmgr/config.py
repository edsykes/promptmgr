import json
import os
from typing import Dict

CONFIG_FILE = os.path.join(os.path.expanduser('~'), '.promptmgr.json')
DEFAULT_CONFIG = {
    'prompt_dir': '',
    'llms': {
        'ChatGPT': 'https://chat.openai.com',
    }
}


def load_config() -> Dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()


def save_config(cfg: Dict) -> None:
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2)
