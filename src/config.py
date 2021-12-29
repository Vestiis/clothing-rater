class Config:
    class Ocr:
        pixels_per_image = 400 * 400

    class WordsMatcher:
        similarity_type = "difflib"
        tokenization_type = "split"
        extract_with_multi_process = False
        similarity_threshold = 0.9
