import sys
import importlib
import pytest

import slowapi
from slowapi.util import get_remote_address
from app.config import settings

MODULE_PATH = 'app.rate_limiter'

@pytest.fixture(autouse=True)
def reload_rate_limiter_module(monkeypatch):
    """
    Ensure that changes to environment variables are picked up by reloading the module.
    """

    if MODULE_PATH in sys.modules:
        del sys.modules[MODULE_PATH]
    yield

    if MODULE_PATH in sys.modules:
        del sys.modules[MODULE_PATH]


def test_limiter_instance_and_attrs():

    rate_mod = importlib.import_module(MODULE_PATH)

    assert rate_mod.storage == 'memory://'

    limiter = rate_mod.limiter
    assert isinstance(limiter, slowapi.Limiter)

    assert limiter._key_func is get_remote_address

    assert limiter._storage_uri == rate_mod.storage


def test_redis_uri_from_env(monkeypatch):

    env_name = settings.rate_limit.redis_url
    test_value = 'redis://localhost:6379'
    monkeypatch.setenv(env_name, test_value)

    rate_mod = importlib.import_module(MODULE_PATH)

    assert rate_mod.redis_uri == test_value


def test_load_dotenv_called(monkeypatch):
    fake_called = {'count': 0}

    def fake_load_dotenv(*args, **kwargs):
        fake_called['count'] += 1

    monkeypatch.setenv(settings.rate_limit.redis_url, '')
    monkeypatch.setenv('DUMMY', '1')

    import dotenv
    monkeypatch.setattr(dotenv, 'load_dotenv', fake_load_dotenv)

    assert fake_called['count'] == 1, "load_dotenv should be called once on import"
