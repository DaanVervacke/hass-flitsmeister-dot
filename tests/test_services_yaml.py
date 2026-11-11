"""Tests that services.yaml offers exactly the values the action schemas accept."""

from pathlib import Path

import yaml

from custom_components.flitsmeister_dot.service_actions.play_progress import COLOR_OPTIONS
from custom_components.flitsmeister_dot.service_actions.presets import PRESET_ANIMATIONS

SERVICES_YAML = Path(__file__).parent.parent / "custom_components" / "flitsmeister_dot" / "services.yaml"


def _select_options(action: str, field: str) -> list[str]:
    services = yaml.safe_load(SERVICES_YAML.read_text())
    return services[action]["fields"][field]["selector"]["select"]["options"]


def test_preset_options_match_the_presets() -> None:
    """Every preset in the dropdown plays, and every preset is in the dropdown."""
    assert _select_options("play_animation", "preset") == list(PRESET_ANIMATIONS)


def test_color_options_match_the_colors() -> None:
    """Every color in the dropdown is accepted, and every color is in the dropdown."""
    assert _select_options("play_progress", "color") == COLOR_OPTIONS
