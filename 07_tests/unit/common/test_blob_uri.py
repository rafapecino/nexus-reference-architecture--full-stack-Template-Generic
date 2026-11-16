import pytest

pytestmark = pytest.mark.unit


def test_blob_uri_roundtrip():
    from common.storage.blob import make_blob_uri, parse_blob_uri  # type: ignore

    container = "memorias"
    name = "1234/memoria.json"

    uri = make_blob_uri(container, name)
    c2, n2 = parse_blob_uri(uri)

    assert c2 == container
    assert n2 == name
    # assert uri == f"https://fakestorageaccount.blob.core.windows.net/{container}/{name}"
