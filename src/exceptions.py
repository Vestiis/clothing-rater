class MaterialNotFound(Exception):
    def __str__(self):
        return "No material found"


class MissingMaterialPercentage(Exception):
    def __init__(self, material: str):
        self.material = material

    def __str__(self):
        return f"No percentage found for found material {self.material}"


class CountryNotFound(Exception):
    def __str__(self):
        return "No country found"


class TextNotFound(Exception):
    def __str__(self):
        return "No text found"
