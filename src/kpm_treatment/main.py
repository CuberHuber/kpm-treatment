from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True)
class Greeting:
    """An immutable greeting for a named recipient."""

    name: str

    def message(self) -> str:
        return f"Hello, {self.name}!"
