import os
from typing import List, Optional, Union


class MaterialNotFound(Exception):
    def __init__(self, label: str):
        self.label = label

    def __str__(self):
        return "No material found"


class MissingMaterialPercentage(Exception):
    def __init__(self, material: str, label: str):
        self.label = label
        self.material = material

    def __str__(self):
        return f"No percentage found for found material {self.material}"


class CountryNotFound(Exception):
    def __init__(self, label: str):
        self.label = label

    def __str__(self):
        return "No country found"


class TextNotFound(Exception):
    def __str__(self):
        return "No text found"


class MultipleLabelErrors(Exception):
    def __init__(
        self,
        label: str,
        material_not_found_exc: Optional[MaterialNotFound] = None,
        missing_percentage_excs: Optional[List[MissingMaterialPercentage]] = None,
        country_not_found_exc: Optional[CountryNotFound] = None,
    ):
        self.label = label
        self.material_not_found_exc = material_not_found_exc
        self.missing_percentage_excs = missing_percentage_excs
        self.country_not_found_exc = country_not_found_exc

    @property
    def missing_percentage_message(self) -> str:
        if not self.missing_percentage_excs:
            return None
        return (
            f"No percentage found for found materials "
            f"{', '.join(exception.material for exception in self.missing_percentage_excs)}"
        )

    @property
    def material_not_found_message(self) -> str:
        if not self.material_not_found_exc:
            return None
        return str(self.material_not_found_exc)

    @property
    def country_not_found_message(self) -> str:
        if not self.country_not_found_exc:
            return None
        return str(self.country_not_found_exc)

    def __str__(self):
        messages = []
        if self.missing_percentage_message:
            messages.append(self.missing_percentage_message)
        if self.material_not_found_message:
            messages.append(self.material_not_found_message)
        if self.country_not_found_message:
            messages.append(self.country_not_found_message)
        return f".{os.linesep}".join(messages)
