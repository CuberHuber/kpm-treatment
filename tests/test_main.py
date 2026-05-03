from dataclasses import FrozenInstanceError

import pytest

from kpm_treatment.main import Greeting


@pytest.mark.unit
def test_greeting_message() -> None:
    greeting = Greeting(name="World")
    assert greeting.message() == "Hello, World!"


@pytest.mark.unit
def test_greeting_is_immutable() -> None:
    greeting = Greeting(name="Alice")
    with pytest.raises(FrozenInstanceError):
        greeting.name = "Bob"  # type: ignore[misc]
