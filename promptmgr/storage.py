import os
from datetime import datetime
from typing import List
from .models import Prompt

VERSION_MARK = "---version:"

class FileLock:
    """Simple file lock using a sidecar .lock file."""
    def __init__(self, path: str):
        self.lock_path = path + '.lock'

    def __enter__(self):
        # create lock file exclusively
        fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        return self

    def __exit__(self, exc_type, exc, tb):
        if os.path.exists(self.lock_path):
            os.remove(self.lock_path)


def _format_metadata(prompt: Prompt) -> str:
    return (
        "---\n"
        f"id: {prompt.id}\n"
        f"name: {prompt.name}\n"
        f"description: {prompt.description}\n"
        f"tags: {', '.join(prompt.tags)}\n"
        "---\n"
    )


def save_prompt(prompt: Prompt, filepath: str) -> None:
    """Save a prompt to a markdown file with version history."""
    history: List[dict] = []
    if os.path.exists(filepath):
        existing = load_prompt(filepath)
        timestamp = datetime.utcnow().isoformat()
        history = [
            {"timestamp": timestamp, "content": existing.content}
        ] + existing.history
    if prompt.history:
        history = prompt.history + history
    with FileLock(filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(_format_metadata(prompt))
            f.write(prompt.content.rstrip() + "\n")
            for entry in history:
                f.write(f"{VERSION_MARK}{entry['timestamp']}---\n")
                f.write(entry['content'].rstrip() + "\n")


def load_prompt(filepath: str) -> Prompt:
    with open(filepath, 'r', encoding='utf-8') as f:
        data = f.read()
    sections = data.split('---\n', 2)
    if len(sections) < 3:
        raise ValueError('Invalid prompt file')
    meta_block, rest = sections[1], sections[2]
    metadata = {}
    for line in meta_block.strip().splitlines():
        key, _, value = line.partition(':')
        metadata[key.strip()] = value.strip()
    # split current content and versions
    parts = rest.split(VERSION_MARK)
    content = parts[0].rstrip()
    history = []
    for part in parts[1:]:
        ts, _, body = part.partition('---\n')
        history.append({'timestamp': ts.strip(), 'content': body.rstrip()})
    return Prompt(
        id=metadata.get('id', ''),
        name=metadata.get('name', ''),
        description=metadata.get('description', ''),
        tags=[t.strip() for t in metadata.get('tags', '').split(',') if t.strip()],
        content=content,
        history=history,
    )
