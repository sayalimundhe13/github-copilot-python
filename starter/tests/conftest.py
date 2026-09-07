import pytest

import app as app_module


@pytest.fixture
def client():
    app_module.CURRENT['puzzle'] = None
    app_module.CURRENT['solution'] = None
    app_module.app.config.update(TESTING=True)

    with app_module.app.test_client() as test_client:
        yield test_client

    app_module.CURRENT['puzzle'] = None
    app_module.CURRENT['solution'] = None
