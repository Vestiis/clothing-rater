"""

This script allows to simulate a load of concurrent requests trying to reach the
same endpoint at the same time.
"""

import os
import time
from multiprocessing.dummy import Pool

import requests

from src.app.routes.score import RouteType
from src.meta.request import post_compute_score


def cut_in_sub_lists(elems, chunk_size):
    chunk_size = max(1, chunk_size)
    return list(elems[i : i + chunk_size] for i in range(0, len(elems), chunk_size))


API_URL = "http://localhost"
API_PORT = 5001
# API_URL = os.environ["API_URL"]
# API_PORT = 8080
REQUESTS_AMOUNT = 200
# REQUESTS_PER_SECOND = 10
REQUESTS_PER_SECOND = REQUESTS_AMOUNT
IMAGES_PER_REQUEST_AMOUNT = 1
# MAX_CONCURRENT_REQUESTS = 20
MAX_CONCURRENT_REQUESTS = 100
IMAGE_URL = (
    "https://static9.depositphotos.com/1011514/1077/i/950/"
    "depositphotos_10773191-stock-photo-clothing-label.jpg"
)

if __name__ == "__main__":
    images_per_request = cut_in_sub_lists(
        [requests.get(IMAGE_URL).content] * REQUESTS_AMOUNT * IMAGES_PER_REQUEST_AMOUNT,
        chunk_size=IMAGES_PER_REQUEST_AMOUNT,
    )
    batches_images_per_request = cut_in_sub_lists(
        images_per_request,
        chunk_size=min(MAX_CONCURRENT_REQUESTS, len(images_per_request)),
    )
    for batch_idx, batch_images_per_request in enumerate(batches_images_per_request):
        pool = Pool(len(batch_images_per_request))
        async_results = []
        requests_per_second_start = time.time()
        for i, request_images in enumerate(batch_images_per_request):
            async_results.append(
                pool.apply_async(
                    post_compute_score,
                    (request_images, RouteType.post_compute_score_from_image_bytes,),
                    {"api_url": API_URL, "api_port": API_PORT},
                )
            )
            print(
                f"Async batch {batch_idx + 1} / {len(batches_images_per_request)} "
                f"Done {i + 1} / {len(batch_images_per_request)}"
            )
            if (i + 1) % REQUESTS_PER_SECOND == 0:
                requests_per_second_end = time.time()
                if requests_per_second_end - requests_per_second_start < 1:
                    time.sleep(
                        1 - (requests_per_second_end - requests_per_second_start)
                    )
                requests_per_second_start = time.time()

        for i, async_result in enumerate(async_results):
            try:
                # For each future, wait until the request is finished
                # and then print the response object.
                print("there0")
                print(async_result.get())
                print("there1")
            except requests.exceptions.ReadTimeout:
                print(f"{i}th batch of requests encounters a timeout issue")
