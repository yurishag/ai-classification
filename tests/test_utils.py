import logging
import re

from app.utils import setup_logging, logger

def pytest_configure(config):
    
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.root.setLevel(logging.NOTSET)


def test_setup_logging_calls_basicConfig(monkeypatch):
    called = {}
    def fake_basicConfig(**kwargs):
        called['kwargs'] = kwargs
    monkeypatch.setattr(logging, 'basicConfig', fake_basicConfig)

    setup_logging()

    assert 'kwargs' in called, "basicConfig should be called"
    assert called['kwargs']['format'] == '%(asctime)s - %(levelname)s - %(message)s'
    assert called['kwargs']['level'] == logging.INFO


def test_logging_output_format_and_level(capsys):

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    setup_logging()

    test_message = 'hello world'
    logger.info(test_message)

    captured = capsys.readouterr()
    err = captured.err.strip()

    pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - INFO - hello world"
    assert re.match(pattern, err), f"Log output '{err}' does not match expected format"


def test_logging_level_effective(capsys):
    
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    setup_logging()

    logger.debug('debug message')
    logger.info('info message')

    captured = capsys.readouterr()
    out = captured.err
    assert 'debug message' not in out
    assert 'info message' in out
