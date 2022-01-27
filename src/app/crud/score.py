from typing import List, Optional, Tuple, Union

from src.exceptions import CountryNotFound, MaterialNotFound, MissingMaterialPercentage
from src.interpreter import Interpreter, LabelCountry, LabelMaterial
from src.scorer import GlobalScore, Scorer


def handle_material_exceptions(found_materials: List[LabelMaterial]):
    if not found_materials:
        raise MaterialNotFound
    for material in found_materials:
        if material.percentage is None:
            raise MissingMaterialPercentage(material=material.names[0])
    # if sum(material.percentage for material in materials) < 100:
    # raise MissingMaterials("Missing materials, less than 100% composition")


# dummy
def handle_country_exceptions(found_country: Optional[LabelCountry]):
    if found_country is None:
        raise CountryNotFound


def handle_interpreter_exceptions(
    found_materials: List[LabelMaterial], found_country: Optional[LabelCountry]
):
    handle_material_exceptions(found_materials=found_materials)
    handle_country_exceptions(found_country=found_country)


def compute_score(
    label: str,
    interpreter: Interpreter,
    environment_ranking: float,
    societal_ranking: float,
    animal_ranking: float,
    health_ranking: float,
    return_found_elements: bool = False,
) -> Union[GlobalScore, Tuple[GlobalScore, List[LabelMaterial], List[LabelCountry]]]:
    found_materials = interpreter.find_materials(label=label)
    found_country = interpreter.find_country(label=label)
    handle_interpreter_exceptions(
        found_materials=found_materials, found_country=found_country
    )
    score = Scorer(
        environment_ranking=environment_ranking,
        societal_ranking=societal_ranking,
        animal_ranking=animal_ranking,
        health_ranking=health_ranking,
    )(country=found_country, materials=found_materials)
    if return_found_elements:
        return score, found_materials, found_country
    return score
