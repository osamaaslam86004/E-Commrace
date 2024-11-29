import pytest


@pytest.mark.usefixtures("celery_session_app")
def test_celery_redis_setup(celery_session_app):
    # Assert that the broker is set to Redis
    assert (
        celery_session_app.conf.broker_url == "redis://localhost:6379/0"
    ), f"Expected Redis broker URL, but got {celery_session_app.conf.broker_url}"

    # Assert that the result backend is set to Redis
    assert (
        celery_session_app.conf.result_backend == "redis://localhost:6379/0"
    ), f"Expected Redis result backend, but got {celery_session_app.conf.result_backend}"


@pytest.mark.usefixtures("celery_session_worker")
def test_celery_worker_concurrency(celery_session_worker):
    # Assert that the concurrency is set to 1
    assert celery_session_worker.concurrency == 1
