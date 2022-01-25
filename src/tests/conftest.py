import pytest

from src.interpreter import Interpreter, get_interpreter
from src.words_matcher.words_matcher import get_words_matcher


@pytest.fixture()
def interpreter() -> Interpreter:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """
    yield get_interpreter(words_matcher=get_words_matcher())
