from typing import List

import pytest

from src.interpreter import Interpreter
from tests.conftest import COUNTRIES, LABELS, MATERIALS_NAMES


@pytest.mark.parametrize("materials_names, label", list(zip(MATERIALS_NAMES, LABELS)))
def test_interpreter_find_materials(
    interpreter: Interpreter, materials_names: List[str], label: str
):
    materials_names = [
        Interpreter._standardize_material_name(material_name)
        for material_name in materials_names
    ]
    materials = interpreter.find_materials(label)
    for material in materials:
        material.names = [
            Interpreter._standardize_material_name(name) for name in material.names
        ]
    for material in materials:
        assert any(name in materials_names for name in material.names)
    for material_name in materials_names:
        assert any(material_name in material.names for material in materials)


@pytest.mark.parametrize("country, label", list(zip(COUNTRIES, LABELS)))
def test_interpreter_find_country(
    interpreter: Interpreter, country: List[str], label: str
):
    found_country = interpreter.find_country(label=label)
    if found_country is not None or country is not None:
        assert Interpreter._standardize_country_name(country) in [
            Interpreter._standardize_country_name(name) for name in found_country.names
        ]
