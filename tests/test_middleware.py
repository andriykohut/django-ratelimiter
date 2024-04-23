from tests.utils import wait_for_rate_limit


def test_middleware(client):
    assert wait_for_rate_limit('/test-middleware/hit/') == 3
    for _ in range(5):
        response = client.get('/test-middleware/miss/')
        assert response.status_code == 200
