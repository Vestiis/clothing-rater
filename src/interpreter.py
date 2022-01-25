import json
import os
import re
from typing import List, Optional

from database.api.meta.country import get_all_countries
from database.api.meta.material import get_all_materials
from database.api.schemas.country import Country
from database.api.schemas.material import Material
from fastapi import Depends

from src import DATABASE_API_URL
from src.config import Config
from src.exceptions import (CountryNotFound, MaterialNotFound,
                            MissingMaterialPercentage)
from src.words_matcher.match import MatchFilter
from src.words_matcher.words_matcher import WordsMatcher, get_words_matcher

ADD_SPACE_ELEMENTS = [
    "made in",
    "/",
    "%",
]


class LabelMaterial(Material):
    percentage: Optional[float]

    def __hash__(self):
        return hash(json.dumps(self.dict()))

    def __eq__(self, other: "Material"):
        return json.dumps(self.dict()) == json.dumps(other.dict())


class LabelCountry(Country):
    pass


def handle_material_exceptions(materials: List[LabelMaterial]):
    if not materials:
        raise MaterialNotFound
    for material in materials:
        if material.percentage is None:
            raise MissingMaterialPercentage(material=material.names[0])
    # if sum(material.percentage for material in materials) < 100:
        # raise MissingMaterials("Missing materials, less than 100% composition")


# dummy
def handle_country_exceptions(country: Optional[LabelCountry]):
    if country is None:
        raise CountryNotFound


class Interpreter:
    def __init__(
        self,
        materials: List[Material],
        countries: List[Country],
        similarity_threshold: float = 0.85,
        words_matcher: WordsMatcher = None,
        filter_overlapping_materials_on: str = MatchFilter.longest
    ):
        self.words_matcher = (
            words_matcher
            if words_matcher is not None
            else WordsMatcher(similarity_threshold=similarity_threshold)
        )
        self.materials = materials
        self.countries = countries
        self.filter_overlapping_materials_on = filter_overlapping_materials_on

        self.spelling_to_material: dict = None
        self.spelling_to_country: dict = None
        self.material_names: List[str] = None
        self.country_names: List[str] = None

        self._build()

    @staticmethod
    def _standardize_label(label: str):
        label = label.replace(os.linesep, " ").lower()
        for element in ADD_SPACE_ELEMENTS:
            label = label.replace(element, f" {element} ")
        # replace all trailing whitespaces by a single whitespace
        label = re.sub("[ ]{2,}", " ", label)
        # if "made in" without space next to it then add a space next to it
        # if matches := re.findall("(made in[^ ])", label):
        #     for match in matches:
        #         label = label.replace(match, f"{match[:-1]} {match[-1]}")
        return label

    @staticmethod
    def _standardize_material_name(material_name: str):
        return material_name.lower()

    @staticmethod
    def _standardize_country_name(country_name: str):
        return country_name.lower()

    def _build(self):
        self.spelling_to_material = {
            self._standardize_material_name(spelling): material
            for material in self.materials
            for spelling in material.names
        }
        self.spelling_to_country = {
            self._standardize_country_name(spelling): country
            for country in self.countries
            for spelling in country.names
        }
        self.material_names = list(self.spelling_to_material.keys())
        self.country_names = list(self.spelling_to_country.keys())

    def _find_material_percentage(
        self, label: str, label_material: str, look_left_first: Optional[bool] = None
    ):
        if look_left_first is None:
            look_left_first = True
        expressions = [
            "{}[^0-9]*(\d+) ?%[^0-9]*{}"  # if material and its translations are next to percentage
        ]
        if look_left_first:
            args = ["", label_material]
            found_on_left = True
        else:
            args = [label_material, ""]
            found_on_left = False

        # try look on one side
        for expression in expressions:
            if matches := re.findall(expression.format(*args), label):
                return float(matches[0]), found_on_left

        # try look on the other side
        args = args[::-1]
        found_on_left = not found_on_left
        for expression in expressions:
            if matches := re.findall(expression.format(*args), label):
                return matches[0], found_on_left

        return None, None

    def find_materials(self, label: str):
        label_materials = dict()
        label = self._standardize_label(label)
        matches = self.words_matcher.find_words_in_sentences(
            sentences=[label],
            referential=self.material_names,
            keep_best_same_match=True,
            filter_same_location_match=True,
            filter_same_location_match_on=self.filter_overlapping_materials_on,
        )[0]

        # sort matches from first found in text to last found in text
        matches = sorted(matches, key=lambda match: match.start)
        look_left_first = None
        for match in matches:
            percentage, found_on_left = self._find_material_percentage(
                label=match.sentence,
                label_material=match.matching_sub_sentence,
                look_left_first=look_left_first,
            )
            if found_on_left is not None and look_left_first is None:
                look_left_first = found_on_left

            found_material = self.spelling_to_material.get(match.found_word)
            if found_material not in label_materials:
                label_materials[found_material] = percentage
            elif label_materials[found_material] is None and percentage is not None:
                label_materials[found_material] = percentage

        label_materials = [
            LabelMaterial(**material.dict(), percentage=percentage)
            for material, percentage in label_materials.items()
        ]
        handle_material_exceptions(materials=label_materials)
        return label_materials

    def find_country(self, label: str):
        label = self._standardize_label(label)
        # faire en sorte  de d'abord chercher un terme clé style "made in {country}"
        # avant de procéder autrement

        matches = self.words_matcher.find_words_in_sentences(
            sentences=[label],
            referential=self.country_names,
            keep_best_same_match=True,
            filter_same_location_match=False,
        )[0]
        # select country that is found first in text
        matches = sorted(
            matches, key=lambda match: match.sentence.find(match.matching_sub_sentence)
        )
        if matches:
            country = LabelCountry(
                **self.spelling_to_country[matches[0].found_word].dict()
            )
        else:
            country = None
        handle_country_exceptions(country=country)
        return country


def get_interpreter(
    words_matcher: WordsMatcher = Depends(get_words_matcher),
) -> Interpreter:
    interpreter = Interpreter(
        materials=get_all_materials(
            api_url=DATABASE_API_URL, serialize_as_python_obj=True
        ),
        countries=get_all_countries(
            api_url=DATABASE_API_URL, serialize_as_python_obj=True
        ),
        words_matcher=words_matcher,
        filter_overlapping_materials_on=Config.Interpreter.filter_overlapping_materials_on
    )
    return interpreter
