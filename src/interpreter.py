import json
import os
import re
from typing import List, Optional

import cachetools.func
from database.api.meta.country import get_all_countries
from database.api.meta.material import get_all_materials
from database.api.schemas.country import Country
from database.api.schemas.material import Material
from fastapi import Depends

from src.config import Config
from src.words_matcher.match import MatchFilter
from src.words_matcher.words_matcher import WordsMatcher, get_words_matcher

ADD_SPACE_ELEMENTS = [
    "madein",
    "made in",
    "/",
    "%",
    "-",
]

CANCEL_ELEMENTS = [
    "(",
    ")",
]


class LabelMaterial(Material):
    percentage: Optional[float]

    def __hash__(self):
        return hash(json.dumps(self.dict()))

    def __eq__(self, other: "Material"):
        return json.dumps(self.dict()) == json.dumps(other.dict())


class LabelCountry(Country):
    pass


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

    def _standardize_label(self, label: str):
        label = label.replace(os.linesep, " ").lower()
        for element in CANCEL_ELEMENTS:
            label = label.replace(element, "")
        for element in ADD_SPACE_ELEMENTS:
            label = label.replace(element, f" {element} ")
        # replace all trailing whitespaces by a single whitespace
        label = re.sub("[ ]{2,}", " ", label)
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

    @staticmethod
    def _find_material_percentage(
        label: str, label_material: str, look_left_first: Optional[bool] = None
    ):
        if look_left_first is None:
            look_left_first = True
        # a whitespace next to the first digit is enforced, if not the '.*' part would
        # also match the first digits of the percentage
        expressions = [
            "{}.* (\d+) ?%.*{}"  # if material and its translations are next to percentage
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
        return label_materials

    def find_country(self, label: str):
        label = self._standardize_label(label)
        matches = self.words_matcher.find_words_in_sentences(
            sentences=[label],
            referential=self.country_names,
            keep_best_same_match=True,
            filter_same_location_match=False,
        )[0]
        country = None
        # select in priority the country which corresponds to a regex
        # of which we are sure
        for match in matches:
            # check if the part of the sentence corresponding to a country
            # is next to the words 'made in'
            if re.findall(f"made in ?{match.matching_sub_sentence}", label):
                country = LabelCountry(
                    **self.spelling_to_country[match.found_word].dict()
                )
        if matches and country is None:
            # select country that is found first in text
            matches = sorted(
                matches, key=lambda match: match.sentence.find(match.matching_sub_sentence)
            )
            country = LabelCountry(
                **self.spelling_to_country[matches[0].found_word].dict()
            )
        return country


@cachetools.func.ttl_cache(maxsize=None, ttl=float(Config.Inputs.SECONDS_TO_LIVE_DB_REQUEST_CACHE))
def _get_all_materials(api_url: str, serialize_as_python_obj: bool):
    # if materials available through memory store:
    # return memory store materials
    materials = get_all_materials(api_url=api_url, serialize_as_python_obj=serialize_as_python_obj)
    # set memory store materials
    return materials


@cachetools.func.ttl_cache(maxsize=None, ttl=float(Config.Inputs.SECONDS_TO_LIVE_DB_REQUEST_CACHE))
def _get_all_countries(api_url: str, serialize_as_python_obj: bool):
    return get_all_countries(api_url=api_url, serialize_as_python_obj=serialize_as_python_obj)


def get_interpreter(
    words_matcher: WordsMatcher = Depends(get_words_matcher),
) -> Interpreter:
    interpreter = Interpreter(
        materials=_get_all_materials(
            api_url=Config.Inputs.DATABASE_API_URL, serialize_as_python_obj=True
        ),
        countries=_get_all_countries(
            api_url=Config.Inputs.DATABASE_API_URL, serialize_as_python_obj=True
        ),
        words_matcher=words_matcher,
        filter_overlapping_materials_on=Config.Interpreter.filter_overlapping_materials_on
    )
    return interpreter
