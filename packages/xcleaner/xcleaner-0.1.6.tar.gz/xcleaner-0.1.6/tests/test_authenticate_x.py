"""
Unit tests for xcleaner.authenticate_x module.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from xcleaner.authenticate_x import authenticate_x


def test_authenticate_x(monkeypatch):
    """Test authenticate_x returns a DummyAPI instance with monkeypatched tweepy handlers."""
    class DummyAuth:
        pass
    class DummyAPI:
        pass
    def dummy_handler(*_args, **_kwargs):
        return DummyAuth()
    def dummy_api(*_args, **_kwargs):
        return DummyAPI()
    monkeypatch.setattr('tweepy.OAuth1UserHandler', dummy_handler)
    monkeypatch.setattr('tweepy.API', dummy_api)
    api = authenticate_x('k', 's', 't', 'ts')
    assert isinstance(api, DummyAPI)
