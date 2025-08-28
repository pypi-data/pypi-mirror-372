import os

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures")
MOCK_API_URL = "http://panoramax-local.dev"


def pytest_addoption(parser):
    parser.addoption("--external-panoramax-url", action="store")
