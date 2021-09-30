from src.scorer import Scorer
from src.words_matcher import WordsMatcher


def compute_score(
    label: str,
    words_matcher: WordsMatcher,
    ecology_importance: float,
    societal_importance: float,
):
    return Scorer(
        ecology_importance=ecology_importance,
        societal_importance=societal_importance,
        words_matcher=words_matcher,
    )(label)
