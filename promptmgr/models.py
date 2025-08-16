from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Prompt:
    """Represents a prompt with metadata and content."""
    id: str
    name: str
    description: str
    tags: List[str]
    content: str
    history: List[Dict[str, str]] = field(default_factory=list)

    @property
    def metadata(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
        }
