from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._client import AsyncHaize, Haize


class SyncAPIResource:
    _client: Haize

    def __init__(self, client: Haize) -> None:
        self._client = client

        self._get = client.get
        self._post = client.post


class AsyncAPIResource:
    _client: AsyncHaize

    def __init__(self, client: AsyncHaize) -> None:
        self._client = client

        self._get = client.get
        self._post = client.post
