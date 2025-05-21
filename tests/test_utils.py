import logging
import pytest
from logging import Logger
import importlib

module_name = "app.main"
mymodule = importlib.import_module(module_name)
setup_logging = mymodule.setup_logging
logger = mymodule.logger

def test_setup_logging_invokes_basicConfig(monkeypatch):
    called = {}
    def fake_basicConfig(**kwargs):
        called.update(kwargs)
    monkeypatch.setattr(logging, 'basicConfig', fake_basicConfig)
    setup_logging()
    assert called.get('format') == '%(asctime)s - %(levelname)s - %(message)s'
    assert called.get('level') == logging.INFO

def test_logger_instance_and_name():
    assert isinstance(logger, Logger)
    assert logger.name == module_name

def test_logger_info_enabled_after_setup():
    setup_logging()
    assert logger.isEnabledFor(logging.INFO)
    assert not logger.isEnabledFor(logging.DEBUG)

