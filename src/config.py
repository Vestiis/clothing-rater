import os


class Config:
    class Ocr:
        # advised nb pixels by Google:
        # https://cloud.google.com/vision/docs/supported-files
        pixels_per_image = 640 * 480
        # pixels_per_image = 640 * 480 * 2

    class WordsMatcher:
        similarity_type = "difflib"
        tokenization_type = "split"
        extract_with_multi_process = False
        similarity_threshold = 0.9

    class Interpreter:
        filter_overlapping_materials_on = "longest"

    class Inputs:
        DATABASE_API_URL = os.environ.get("DATABASE_API_URL")
        SECONDS_TO_LIVE_DB_REQUEST_CACHE = os.environ.get(
            "SECONDS_TO_LIVE_DB_REQUEST_CACHE"
        )
