import logging

import pytest

pytestmark = pytest.mark.unit


def test_setup_logging_does_not_crash(set_env, caplog):
    set_env("LOG_LEVEL", "INFO")

    from common.logging import setup_logging  # ajusta import si tu módulo se llama distinto

    setup_logging()

    with caplog.at_level(logging.INFO):
        logging.getLogger("test").info("hello")

    assert any("hello" in r.message for r in caplog.records)
