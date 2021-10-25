import json
import os
import re
from dataclasses import dataclass
from typing import List, Optional

from database.api.meta.country import get_all_countries
from database.api.meta.material import get_all_materials
from database.api.schemas.country import Country
from database.api.schemas.material import Material
from fastapi import Depends

from src import DATABASE_API_URL
from src.exceptions import (CountryNotFound, MaterialNotFound,
                            MissingMaterialPercentage)
from src.words_matcher import WordsMatcher, get_words_matcher


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


# dummy
def handle_country_exceptions(country: Optional[LabelCountry]):
    if country is None:
        raise CountryNotFound


def standardize(label: str):
    return label.replace(os.linesep, " ")


class Interpreter:
    def __init__(
        self,
        materials: List[Material],
        countries: List[Country],
        similarity_threshold: float = 0.85,
        words_matcher: WordsMatcher = None,
    ):
        self.words_matcher = (
            words_matcher
            if words_matcher is not None
            else WordsMatcher(similarity_threshold=similarity_threshold)
        )
        self.materials = materials
        self.countries = countries

        self.spelling_to_material: dict = None
        self.spelling_to_country: dict = None
        self.material_names: List[str] = None
        self.country_names: List[str] = None

        self._build()

    def _build(self):
        self.spelling_to_material = {
            spelling: material
            for material in self.materials
            for spelling in material.names
        }
        self.spelling_to_country = {
            spelling: country
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
            "{} ?(\d+) ?% ?{}",  # if material next to percentage
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
                return matches[0], found_on_left

        # try look on the other side
        args = args[::-1]
        found_on_left = not found_on_left
        for expression in expressions:
            if matches := re.findall(expression.format(*args), label):
                return matches[0], found_on_left

        return None, None

    def find_materials(self, label: str):
        label_materials = dict()
        label = standardize(label)
        matches = self.words_matcher.find_words_in_sentences(
            sentences=[label], referential=self.material_names
        )[0]
        matches = self.words_matcher.filter_best_matches(matches)
        # sort matches from first found in text in last in text
        matches = sorted(
            matches, key=lambda match: match.sentence.find(match.matching_sub_sentence)
        )
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
        label = standardize(label)
        matches = self.words_matcher.find_words_in_sentences(
            sentences=[label], referential=self.country_names
        )[0]
        matches = self.words_matcher.filter_best_matches(matches)
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


def get_interpreter(words_matcher: WordsMatcher = Depends(get_words_matcher)) -> Interpreter:
    interpreter = Interpreter(
        materials=get_all_materials(
            api_url=DATABASE_API_URL, serialize_as_python_obj=True
        ),
        countries=get_all_countries(
            api_url=DATABASE_API_URL, serialize_as_python_obj=True
        ),
        words_matcher=words_matcher
    )
    return interpreter
