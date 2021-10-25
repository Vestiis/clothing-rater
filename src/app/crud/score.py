from typing import List, Tuple, Union

from src.interpreter import Interpreter, LabelCountry, LabelMaterial
from src.scorer import GlobalScore, Scorer


def compute_score(
    label: str,
    interpreter: Interpreter,
    environment_ranking: float,
    societal_ranking: float,
    animal_ranking: float,
    health_ranking: float,
    return_found_elements: bool = False,
) -> Union[GlobalScore, Tuple[GlobalScore, List[LabelMaterial], List[LabelCountry]]]:
    label_materials = interpreter.find_materials(label=label)
    label_country = interpreter.find_country(label=label)
    score = Scorer(
        environment_ranking=environment_ranking,
        societal_ranking=societal_ranking,
        animal_ranking=animal_ranking,
        health_ranking=health_ranking,
    )(country=label_country, materials=label_materials)
    if return_found_elements:
        return score, label_materials, label_country
    return score
