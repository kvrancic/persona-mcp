"""
File storage module for persona knowledge bases.

Handles saving and loading scraped content to/from disk.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List


class PersonaStorage:
    """Manages file-based storage for persona knowledge bases."""

    def __init__(self, base_dir: str = "./knowledge_base"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    def _get_persona_dir(self, person_name: str) -> Path:
        """Get the directory path for a specific persona."""
        # Normalize the person name to a valid directory name
        normalized_name = person_name.lower().replace(" ", "_")
        persona_dir = self.base_dir / normalized_name
        persona_dir.mkdir(exist_ok=True)
        return persona_dir

    def _get_content_dir(self, person_name: str) -> Path:
        """Get the content directory for a specific persona."""
        content_dir = self._get_persona_dir(person_name) / "content"
        content_dir.mkdir(exist_ok=True)
        return content_dir

    def _get_metadata_path(self, person_name: str) -> Path:
        """Get the metadata file path for a specific persona."""
        return self._get_persona_dir(person_name) / "metadata.json"

    def save_content(self, person_name: str, url: str, content: str) -> str:
        """
        Save scraped content to disk.

        Args:
            person_name: Name of the persona
            url: Source URL of the content
            content: The scraped text content

        Returns:
            The hash ID of the saved content
        """
        # Create a hash of the URL for the filename
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]

        # Save the content
        content_dir = self._get_content_dir(person_name)
        content_file = content_dir / f"{url_hash}.txt"
        content_file.write_text(content, encoding="utf-8")

        # Update metadata
        metadata = self._load_metadata(person_name)
        metadata[url_hash] = {
            "url": url,
            "char_count": len(content),
            "file": f"content/{url_hash}.txt"
        }
        self._save_metadata(person_name, metadata)

        return url_hash

    def load_all_content(self, person_name: str) -> List[str]:
        """
        Load all content chunks for a persona.

        Args:
            person_name: Name of the persona

        Returns:
            List of content strings
        """
        content_dir = self._get_content_dir(person_name)

        if not content_dir.exists():
            return []

        contents = []
        for content_file in content_dir.glob("*.txt"):
            text = content_file.read_text(encoding="utf-8")
            contents.append(text)

        return contents

    def _load_metadata(self, person_name: str) -> Dict:
        """Load metadata for a persona."""
        metadata_path = self._get_metadata_path(person_name)

        if metadata_path.exists():
            with open(metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)

        return {}

    def _save_metadata(self, person_name: str, metadata: Dict):
        """Save metadata for a persona."""
        metadata_path = self._get_metadata_path(person_name)

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    def persona_exists(self, person_name: str) -> bool:
        """Check if a persona has been initialized."""
        persona_dir = self._get_persona_dir(person_name)
        metadata_path = self._get_metadata_path(person_name)

        return persona_dir.exists() and metadata_path.exists()

    def get_persona_stats(self, person_name: str) -> Dict:
        """Get statistics about a persona's knowledge base."""
        if not self.persona_exists(person_name):
            return {"exists": False}

        metadata = self._load_metadata(person_name)
        total_chars = sum(item.get("char_count", 0) for item in metadata.values())

        return {
            "exists": True,
            "num_documents": len(metadata),
            "total_chars": total_chars,
            "urls": [item.get("url", "") for item in metadata.values()]
        }
