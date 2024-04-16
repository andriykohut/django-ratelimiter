from typing import Optional

from django.test import Client


def wait_for_rate_limit(
    url: str,
    method: str = "GET",
    client: Optional[Client] = None,
    status: int = 429,
    ok_status: int = 200,
) -> int:
    client = client or Client()
    count = 0
    func = getattr(client, method.lower())
    while True:
        response = func(url)
        if response.status_code == status:
            break
        elif response.status_code != ok_status:
            raise Exception(f"{response.status_code}: {response.content}")
        count += 1
    return count
