from backend.main import app


def test_backend_imports():
    assert app is not None
