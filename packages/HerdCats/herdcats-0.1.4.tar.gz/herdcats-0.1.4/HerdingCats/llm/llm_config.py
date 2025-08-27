from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMCatalogueSummary(Protocol):
    """Protocol defining the interface for catalogue summarizers."""

    def summarise_catalogue(self, catalogue_data) -> dict:
        """Implement the logic to summarise the catalogue data."""
        ...
