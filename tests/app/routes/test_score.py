import json
from typing import Optional

import pytest
from fastapi.testclient import TestClient

import src.app.routes.score
from src.app.api import APP_PREFIX, app
from src.app.schemas.score import LabelMessage
from src.meta.request import build_full_route
from src.scorer import Preference
from tests.conftest import LABELS


def assert_post_compute_score_from_label_message(
    client: TestClient, label_message: LabelMessage, expected_code: Optional[int] = None
):
    response = client.post(
        f"http://localhost:8080"
        f"{build_full_route(api_app_prefix=APP_PREFIX, router_prefix=src.app.routes.score.router.prefix, route=src.app.routes.score.Route.post_compute_score)}",
        data=json.dumps(label_message.dict()),
    )
    if expected_code is not None:
        assert response.status_code == expected_code
    else:
        # Check that everything went well or that one of the anticipated errors occurred
        assert response.status_code in (200, 422)
    return response


@pytest.mark.parametrize(
    "images_urls, expected_code",
    [
        (["https://storage.googleapis.com/public-labels/IMG_5453.JPEG"], 200),
        (["https://storage.googleapis.com/public-labels/IMG_5485.JPEG"], 200),
    ],
)
def test_post_compute_score_from_urls(
    client: TestClient, images_urls: str, expected_code: str
):
    assert_post_compute_score_from_label_message(
        client=client,
        label_message=LabelMessage(
            user_id="dummy",
            preferences=Preference.to_list(random_order=True),
            images_urls=images_urls,
        ),
        expected_code=expected_code,
    )


@pytest.mark.parametrize("label", LABELS)
def test_post_compute_score_from_labels(client: TestClient, label: str):
    assert_post_compute_score_from_label_message(
        client=client,
        label_message=LabelMessage(
            user_id="dummy",
            preferences=Preference.to_list(random_order=True),
            images_labels=[label],
        ),
    )
