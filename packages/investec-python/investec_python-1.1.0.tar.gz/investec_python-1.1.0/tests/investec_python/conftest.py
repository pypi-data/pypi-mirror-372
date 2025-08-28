import pytest

import investec_python


@pytest.fixture(scope="session")
def investec_client() -> investec_python.Investec:
    client = investec_python.Investec(use_sandbox=True, debug=True)
    return client
