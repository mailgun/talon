import pytest
import talon

@pytest.fixture(scope="session", autouse=True)
def initialize_talon_for_tests():
    talon.init() 