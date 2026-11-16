import pytest


@pytest.fixture
def set_env(monkeypatch):
    """
    Helper para setear variables de entorno dentro de un test.
    Uso:
        set_env("FOO", "bar")
    """

    def _set(key: str, value: str):
        monkeypatch.setenv(key, value)

    return _set


@pytest.fixture(autouse=True)
def _clear_settings_cache():
    """
    Si common.config expone un get_settings() cacheado (lru_cache),
    limpiamos el cache antes y después de cada test para evitar contaminación.
    """
    try:
        from common.config.settings import get_settings  # type: ignore
    except Exception:
        yield
        return

    cache_clear = getattr(get_settings, "cache_clear", None)
    if callable(cache_clear):
        cache_clear()

    yield

    if callable(cache_clear):
        cache_clear()
