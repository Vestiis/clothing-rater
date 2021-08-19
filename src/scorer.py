from dataclasses import dataclass
from statistics import mean
from typing import List, Optional

import pandas as pd
from sqlalchemy.orm import Session

from src.db.crud.country import get_countries_as_dataframe
from src.db.crud.material import get_materials, get_materials_as_dataframe
from src.db.database import get_db
from src.db.schemas.country import Country
from src.db.schemas.material import Material
from src.words_matcher import WordsMatcher

HIGHER_IS_SOCIALLY_BETTER = [
    f"{Country.situation}".split(".")[1],
    f"{Country.corruption}".split(".")[1],
    f"{Country.human_freedom_index}".split(".")[1],
    f"{Country.global_food_security_index}".split(".")[1],
    f"{Country.minimum_monthly_salary}".split(".")[1],
]
HIGHER_IS_SOCIALLY_WORSE = [
    f"{Country.poverty_rate}".split(".")[1],
]
HIGHER_IS_ECOLOGY_BETTER = [
    f"{Material.is_recyclable}".split(".")[1],
    f"{Material.skin_friendlyness}".split(".")[1],
]
HIGHER_IS_ECOLOGY_WORSE = [
    f"{Material.health_harmfulness}".split(".")[1],
]
# todo: check why column is named health_harmfulness and a high score there
# todo: leads to a high overall score
# todo: the column is possibly wrongly named


@dataclass
class InterpretedScore:
    score: float


def get_score_relative_to_other_elements(
    element: pd.Series,
    other_elements: pd.DataFrame,
    positive_columns: List[str],
    negative_columns: List[str],
):
    # each row is a different element and a serie
    mins, maxs = other_elements.min(axis=0), other_elements.max(axis=0)
    # keep only used columns
    element = element.loc[positive_columns + negative_columns]
    element[positive_columns] = (element[positive_columns] - mins[positive_columns]) / (
        maxs[positive_columns] - mins[positive_columns]
    )
    element[negative_columns] = (maxs[negative_columns] - element[negative_columns]) / (
        maxs[negative_columns] - mins[negative_columns]
    )
    return element.mean(skipna=True)


class Scorer:
    def __init__(
        self,
        ecology_importance: float = 1,
        societal_importance: float = 1,
        db: Optional[Session] = None,
        words_matcher: Optional[WordsMatcher] = None,
    ):
        self.ecology_importance = ecology_importance
        self.societal_importance = societal_importance
        self.db = db if db is not None else next(get_db())
        self.words_matcher = (
            words_matcher if words_matcher is not None else WordsMatcher()
        )
        self.df_countries = get_countries_as_dataframe(db=self.db).set_index("name")
        self.df_materials = get_materials_as_dataframe(db=self.db).set_index("name")

    def get_material_score(self, material: pd.Series) -> float:
        return get_score_relative_to_other_elements(
            element=material,
            other_elements=self.df_materials,
            positive_columns=HIGHER_IS_ECOLOGY_BETTER,
            negative_columns=HIGHER_IS_ECOLOGY_WORSE,
        )

    def ecology_score(self, label: str) -> float:
        materials = get_materials(db=self.db)
        materials_in_label = set(
            self.words_matcher.similar_referential_words_per_sentence(
                sentences=[label], referential=[x.name for x in materials]
            )[0][0]
        )
        return mean(
            [
                self.get_material_score(material=self.df_materials.loc[material_name])
                for material_name in materials_in_label
            ]
        )

    def get_country_score(self, country: pd.Series) -> float:
        return get_score_relative_to_other_elements(
            element=country,
            other_elements=self.df_countries,
            positive_columns=HIGHER_IS_SOCIALLY_BETTER,
            negative_columns=HIGHER_IS_SOCIALLY_WORSE,
        )

    def societal_score(self, label: str) -> float:
        countries_in_label = set(
            self.words_matcher.similar_referential_words_per_sentence(
                sentences=[label], referential=[x for x in self.df_countries.index]
            )[0][0]
        )
        return mean(
            [
                self.get_country_score(country=self.df_countries.loc[country_name])
                for country_name in countries_in_label
            ]
        )

    def __call__(self, label: str):
        # the scale on which ecology_importance and societal_importance is meaningless
        # the only thing that matters is the multiplication factor from one to the other
        return (
            self.ecology_importance * self.ecology_score(label)
            + self.societal_importance * self.societal_score(label)
        ) / (self.ecology_importance + self.societal_importance)


def get_scorer():
    pass
