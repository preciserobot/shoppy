import pytest
from app.redis import DB

def pytest_addoption(parser):
    parser.addoption("--flush", action="store_true", help="Flush the database before running tests")

@pytest.hookimpl()
def pytest_sessionstart(session):
    if session.config.getoption("--flush"):
        print("Flushing the database before running tests...")
        DB().flush()
