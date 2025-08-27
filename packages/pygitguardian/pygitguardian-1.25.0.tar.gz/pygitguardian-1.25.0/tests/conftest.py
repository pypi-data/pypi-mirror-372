import os
from os.path import dirname, join, realpath
from typing import Any

import pytest
import vcr

from pygitguardian import GGClient


my_vcr = vcr.VCR(
    cassette_library_dir=join(dirname(realpath(__file__)), "cassettes"),
    path_transformer=vcr.VCR.ensure_suffix(".yaml"),
    decode_compressed_response=True,
    ignore_localhost=True,
    match_on=["method", "url"],
    serializer="yaml",
    record_mode="once",
    filter_headers=["Authorization"],
)


def create_client(**kwargs: Any) -> GGClient:
    """Create a GGClient using $GITGUARDIAN_API_KEY"""
    api_key = os.environ["GITGUARDIAN_API_KEY"]
    return GGClient(api_key=api_key, **kwargs)


@pytest.fixture
def client():
    return create_client()
