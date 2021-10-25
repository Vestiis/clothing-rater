from typing import List

from pydantic import BaseModel

from src.interpreter import LabelCountry, LabelMaterial


class Criteria:
    environment = "environment"
    societal = "societal"
    animal = "animal"
    health = "health"


class AnimalScore(BaseModel):
    value: float


class EnvironmentScore(BaseModel):
    value: float
    nature: float
    destruction: float
    water: float


class HealthScore(BaseModel):
    value: float
    treatment: float
    benef: float


class SocietalScore(BaseModel):
    value: float
    politique: float
    human_rights: float
    work: float


class GlobalScore(BaseModel):
    value: float
    societal_score: SocietalScore
    health_score: HealthScore
    environment_score: EnvironmentScore
    animal_score: AnimalScore


class Scorer:
    def __init__(
        self,
        environment_ranking: float,
        societal_ranking: float,
        health_ranking: float,
        animal_ranking: float,
    ):
        self.environment_ranking = environment_ranking
        self.societal_ranking = societal_ranking
        self.health_ranking = health_ranking
        self.animal_ranking = animal_ranking

    @property
    def environment_importance(self):
        return 1 / self.environment_ranking

    @property
    def societal_importance(self):
        return 1 / self.societal_ranking

    @property
    def health_importance(self):
        return 1 / self.health_ranking

    @property
    def animal_importance(self):
        return 1 / self.animal_ranking

    def get_health_score(self, materials: List[LabelMaterial]):
        materials = [x for x in materials if x.percentage is not None]
        sum_weights = sum(x.percentage for x in materials)
        return HealthScore(
            value=sum(x.health * x.percentage for x in materials) / sum_weights,
            treatment=sum(x.treatment * x.percentage for x in materials) / sum_weights,
            benef=sum(x.benef * x.percentage for x in materials) / sum_weights,
        )

    def get_animal_score(self, materials: List[LabelMaterial]):
        materials = [x for x in materials if x.percentage is not None]
        sum_weights = sum(x.percentage for x in materials)
        return AnimalScore(
            value=sum(x.animal * x.percentage for x in materials) / sum_weights,
        )

    def get_environment_score(self, materials: List[LabelMaterial]):
        materials = [x for x in materials if x.percentage is not None]
        sum_weights = sum(x.percentage for x in materials)
        return EnvironmentScore(
            value=sum(x.env * x.percentage for x in materials) / sum_weights,
            nature=sum(x.nature * x.percentage for x in materials) / sum_weights,
            destruction=sum(x.destruction * x.percentage for x in materials)
            / sum_weights,
            water=sum(x.water * x.percentage for x in materials) / sum_weights,
        )

    def get_societal_score(self, country: LabelCountry):
        return SocietalScore(
            value=country.societal,
            politique=country.politique,
            human_rights=country.human_rights,
            work=country.work,
        )

    def __call__(
        self, materials: List[LabelMaterial], country: LabelCountry
    ) -> GlobalScore:
        # the scale on which importances factors are is meaningless
        # the only thing that matters is the multiplication factor from one to the other
        animal_score = self.get_animal_score(materials=materials)
        health_score = self.get_health_score(materials=materials)
        societal_score = self.get_societal_score(country=country)
        environment_score = self.get_environment_score(materials=materials)
        return GlobalScore(
            value=(
                animal_score.value * self.animal_importance
                + health_score.value * self.health_importance
                + societal_score.value * self.societal_importance
                + environment_score.value * self.environment_importance
            )
            / (
                self.animal_importance
                + self.health_importance
                + self.societal_importance
                + self.environment_importance
            ),
            societal_score=societal_score,
            health_score=health_score,
            environment_score=environment_score,
            animal_score=animal_score,
        )
