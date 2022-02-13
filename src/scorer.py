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

    def get_health_score(self, materials: List[LabelMaterial]):
        materials = [x for x in materials if x.percentage is not None]
        sum_weights = sum(x.percentage for x in materials)
        value = sum(x.health * x.percentage for x in materials) / sum_weights
        if self.health_ranking == 1 and value < 100:
            value = (1 - 0.25) * value
        elif self.health_ranking == 2 and value < 75:
            value = (1 - 0.15) * value
        elif self.health_ranking == 3:
            pass
        elif self.health_ranking == 4:
            value = (1 + 0.05) * value
        return HealthScore(
            value=value,
            treatment=sum(x.treatment * x.percentage for x in materials) / sum_weights,
            benef=sum(x.benef * x.percentage for x in materials) / sum_weights,
        )

    def get_animal_score(self, materials: List[LabelMaterial]):
        materials = [x for x in materials if x.percentage is not None]
        sum_weights = sum(x.percentage for x in materials)
        value = sum(x.animal * x.percentage for x in materials) / sum_weights
        if self.health_ranking == 1 and value < 100:
            value = (1 - 0.25) * value
        elif self.health_ranking == 2 and value < 75:
            value = (1 - 0.15) * value
        elif self.health_ranking == 3:
            pass
        elif self.health_ranking == 4:
            value = (1 + 0.05) * value
        return AnimalScore(value=value,)

    def get_environment_score(self, materials: List[LabelMaterial]):
        materials = [x for x in materials if x.percentage is not None]
        sum_weights = sum(x.percentage for x in materials)
        value = sum(x.env * x.percentage for x in materials) / sum_weights
        if self.health_ranking == 1 and value < 100:
            value = (1 - 0.25) * value
        elif self.health_ranking == 2 and value < 75:
            value = (1 - 0.15) * value
        elif self.health_ranking == 3:
            pass
        elif self.health_ranking == 4:
            value = (1 + 0.05) * value
        return EnvironmentScore(
            value=value,
            nature=sum(x.nature * x.percentage for x in materials) / sum_weights,
            destruction=sum(x.destruction * x.percentage for x in materials)
            / sum_weights,
            water=sum(x.water * x.percentage for x in materials) / sum_weights,
        )

    def get_societal_score(self, country: LabelCountry):
        value = country.societal
        if self.health_ranking == 1 and value < 100:
            value = (1 - 0.25) * value
        elif self.health_ranking == 2 and value < 75:
            value = (1 - 0.15) * value
        elif self.health_ranking == 3:
            pass
        elif self.health_ranking == 4:
            value = (1 + 0.05) * value
        return SocietalScore(
            value=value,
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
                animal_score.value
                + health_score.value
                + societal_score.value
                + environment_score.value
            )
            / 4,
            societal_score=societal_score,
            health_score=health_score,
            environment_score=environment_score,
            animal_score=animal_score,
        )
