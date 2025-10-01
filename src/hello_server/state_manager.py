"""
Persona state manager.

Keeps track of the currently active persona across sessions.
"""

from typing import Optional


class PersonaStateManager:
    """Manages the currently active persona."""

    def __init__(self):
        self.current_persona: Optional[str] = None

    def set_persona(self, person_name: str):
        """
        Set the currently active persona.

        Args:
            person_name: Name of the persona to activate
        """
        self.current_persona = person_name

    def get_persona(self) -> Optional[str]:
        """
        Get the currently active persona.

        Returns:
            Name of the current persona, or None if no persona is set
        """
        return self.current_persona

    def has_persona(self) -> bool:
        """
        Check if a persona is currently set.

        Returns:
            True if a persona is active, False otherwise
        """
        return self.current_persona is not None

    def clear_persona(self):
        """Clear the currently active persona."""
        self.current_persona = None
