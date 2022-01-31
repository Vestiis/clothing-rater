from typing import List, Optional, Tuple, Union

from src.exceptions import (
    CountryNotFound,
    MaterialNotFound,
    MissingMaterialPercentage,
    MultipleLabelErrors,
)
from src.interpreter import Interpreter, LabelCountry, LabelMaterial
from src.scorer import GlobalScore, Scorer


def get_material_exceptions(found_materials: List[LabelMaterial]):
    if not found_materials:
        return [MaterialNotFound()]
    return [
        MissingMaterialPercentage(material=material.names[0])
        for material in found_materials
        if material.percentage is None
    ]
    # if sum(material.percentage for material in materials) < 100:
    # raise MissingMaterials("Missing materials, less than 100% composition")


def get_country_exception(found_country: Optional[LabelCountry]):
    if found_country is None:
        return CountryNotFound()


def handle_interpreter_exceptions(
    found_materials: List[LabelMaterial], found_country: Optional[LabelCountry]
):
    exceptions = []
    material_excs = get_material_exceptions(found_materials=found_materials)
    if material_excs:
        exceptions += material_excs
    country_exc = get_country_exception(found_country=found_country)
    if country_exc:
        exceptions.append(country_exc)
    if not exceptions:
        pass
    elif len(exceptions) == 1:
        raise exceptions[0]
    else:
        raise MultipleLabelErrors(
            material_not_found_exc=[
                exc for exc in exceptions if isinstance(exc, MaterialNotFound)
            ][0]
            if any(isinstance(exc, MaterialNotFound) for exc in exceptions)
            else None,
            missing_percentage_excs=[
                exc for exc in exceptions if isinstance(exc, MissingMaterialPercentage)
            ]
            if any(isinstance(exc, MissingMaterialPercentage) for exc in exceptions)
            else None,
            country_not_found_exc=country_exc if country_exc is not None else None,
        )


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
