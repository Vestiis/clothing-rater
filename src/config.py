import os


class Config:
    class Ocr:
        # advised number of pixels by Google:
        # https://cloud.google.com/vision/docs/supported-files
        pixels_per_image = 640 * 480
        # jpeg is lighter than other image format so it is more
        # convenient to sent to Google Vision for speed
        google_image_format = "JPEG"

    class WordsMatcher:
        similarity_type = "difflib"
        tokenization_type = "split"
        extract_with_multi_process = False
        similarity_threshold = 0.875

    class Interpreter:
        filter_overlapping_materials_on = "longest"

    class Inputs:
        DATABASE_API_URL = os.environ.get("DATABASE_API_URL")
        SECONDS_TO_LIVE_DB_REQUEST_CACHE = os.environ.get(
            "SECONDS_TO_LIVE_DB_REQUEST_CACHE"
        )

    class ComputeScore:
        retry_with_google_bounding_polys = True
