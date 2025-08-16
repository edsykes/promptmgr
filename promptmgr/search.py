import re
from fnmatch import fnmatch
from difflib import get_close_matches
from typing import Iterable, List
from .models import Prompt


def search_prompts(prompts: Iterable[Prompt], query: str, *, field: str = 'name', method: str = 'wildcard') -> List[Prompt]:
    """Search prompts by field using different methods."""
    results: List[Prompt] = []
    for prompt in prompts:
        value = getattr(prompt, field) if field != 'tags' else ','.join(prompt.tags)
        if method == 'wildcard':
            if fnmatch(str(value).lower(), query.lower()):
                results.append(prompt)
        elif method == 'regex':
            if re.search(query, str(value)):
                results.append(prompt)
        elif method == 'fuzzy':
            target = str(value) if field != 'tags' else ' '.join(prompt.tags)
            words = target.lower().split()
            if get_close_matches(query.lower(), words, cutoff=0.6):
                results.append(prompt)
    return results
