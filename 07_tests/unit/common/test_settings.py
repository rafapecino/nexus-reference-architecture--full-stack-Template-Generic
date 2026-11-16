import pytest

pytestmark = pytest.mark.unit


def test_settings_reads_env(set_env):
    set_env("AZURE_STORAGE_CONNECTION_STRING", "UseDevelopmentStorage=true")
    set_env("STORAGE_AUTO_CREATE_CONTAINERS", "false")

    set_env("POSTGRES_USER", "postgres")
    set_env("POSTGRES_PASSWORD", "1234")
    set_env("POSTGRES_HOST", "localhost")
    set_env("POSTGRES_PORT", "5432")
    set_env("POSTGRES_DB", "postgres")

    from common.config import get_settings  # type: ignore

    s = get_settings()

    assert s.storage.connection_string == "UseDevelopmentStorage=true"
    assert s.storage.auto_create_containers is False

    assert "postgresql" in str(s.db_work.url)
    assert "localhost:5432" in str(s.db_work.url)
