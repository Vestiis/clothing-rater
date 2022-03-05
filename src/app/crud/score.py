from typing import List, Optional, Tuple, Union

from src.exceptions import (
    CountryNotFound,
    MaterialNotFound,
    MissingMaterialPercentage,
    MultipleLabelErrors,
)
from src.interpreter import Interpreter, LabelCountry, LabelMaterial
from src.ocr import Ocr, OcrBoundingPoly
from src.scorer import GlobalScore, Scorer


def get_material_exceptions(label: str, found_materials: List[LabelMaterial]):
    if not found_materials:
        return [MaterialNotFound(label=label)]
    return [
        MissingMaterialPercentage(label=label, material=material.names[0])
        for material in found_materials
        if material.percentage is None
    ]
    # if sum(material.percentage for material in materials) < 100:
    # raise MissingMaterials("Missing materials, less than 100% composition")


def get_country_exception(label: str, found_country: Optional[LabelCountry]):
    if found_country is None:
        return CountryNotFound(label=label)


def raise_compute_score_exceptions_from_interpreter(
    label: str,
    found_materials: List[LabelMaterial],
    found_country: Optional[LabelCountry],
):
    exceptions = []
    material_excs = get_material_exceptions(
        label=label, found_materials=found_materials
    )
    if material_excs:
        exceptions += material_excs
    country_exc = get_country_exception(label=label, found_country=found_country)
    if country_exc:
        exceptions.append(country_exc)
    if not exceptions:
        pass
    elif len(exceptions) == 1:
        raise exceptions[0]
    else:
        raise MultipleLabelErrors(
            label=label,
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


def ocr_and_compute_images_score(
    ocr: Ocr,
    interpreter: Interpreter,
    environment_ranking: float,
    societal_ranking: float,
    animal_ranking: float,
    health_ranking: float,
    pre_known_labels: Optional[List[str]] = None,
    images_bytes: Optional[List[List[bytes]]] = None,
    google_images_bounding_polys: Optional[List[List[OcrBoundingPoly]]] = None,
    return_found_elements: bool = False,
    retry_with_google_bounding_polys: bool = False,
) -> Union[GlobalScore, Tuple[GlobalScore, List[LabelMaterial], List[LabelCountry]]]:
    if google_images_bounding_polys is None:
        images_labels_and_google_bounding_polys = [
            ocr(image_bytes=image_bytes) for image_bytes in images_bytes
        ]
    else:
        images_labels_and_google_bounding_polys = [
            ocr(image_bytes=image_bytes, image_bounding_polys=google_bounding_polys)
            for image_bytes, google_bounding_polys in zip(
                images_bytes, google_images_bounding_polys
            )
        ]
    label = ""
    if pre_known_labels is not None:
        label += " ".join(pre_known_labels)
    label = f"{label} {' '.join(label for label, _ in images_labels_and_google_bounding_polys)}"
    found_materials = interpreter.find_materials(label=label)
    found_country = interpreter.find_country(label=label)
    try:
        raise_compute_score_exceptions_from_interpreter(
            label=label, found_materials=found_materials, found_country=found_country
        )
    except (
        CountryNotFound,
        MaterialNotFound,
        MissingMaterialPercentage,
        MultipleLabelErrors,
    ) as e:
        # if has not been retried before and retry is wanted then retry
        # else raise exception
        if retry_with_google_bounding_polys:
            return ocr_and_compute_images_score(
                ocr=ocr,
                interpreter=interpreter,
                environment_ranking=environment_ranking,
                societal_ranking=societal_ranking,
                animal_ranking=animal_ranking,
                health_ranking=health_ranking,
                pre_known_labels=pre_known_labels,
                images_bytes=images_bytes,
                google_images_bounding_polys=[
                    bounding_poly
                    for _, bounding_poly in images_labels_and_google_bounding_polys
                ],
                return_found_elements=return_found_elements,
                # very dangerous, force only retry once so not to end up in infinite loop
                # of costly google vision calls
                retry_with_google_bounding_polys=False,
            )
        else:
            raise e
    score = Scorer(
        environment_ranking=environment_ranking,
        societal_ranking=societal_ranking,
        animal_ranking=animal_ranking,
        health_ranking=health_ranking,
    )(country=found_country, materials=found_materials)
    if return_found_elements:
        return score, found_materials, found_country, label
    return score
