import urllib
from typing import Callable, Generator, Optional

from kognic.base_clients.cloud_storage import FileResourceClient
from kognic.base_clients.http_client import HttpClient
from kognic.base_clients.models import CursorIdType


class IOResource:
    def __init__(self, client: HttpClient, file_client: FileResourceClient, workspace_id: str):
        super().__init__()
        self._client = client
        self._file_client = file_client
        self._workspace_id = workspace_id

    def _paginate_get(self, endpoint: str, **kwargs) -> Generator[dict, None, None]:
        yield from self._paginate(self._client.get, endpoint, **kwargs)

    def _paginate_post(self, endpoint: str, **kwargs) -> Generator[dict, None, None]:
        yield from self._paginate(self._client.post, endpoint, **kwargs)

    def _paginate(
        self,
        api_method: Callable,
        endpoint: str,
        next_cursor_id: Optional[CursorIdType] = None,
        **kwargs,
    ) -> Generator[dict, None, None]:
        """
        Paginates through result pages recursively.

        :param api_method: api method to call in the form of a function
        :param endpoint: endpoint to send request to
        :param next_cursor_id: next cursor id to call. Will be appended with the key 'cursorId' to the endpoint
        :param **kwargs: Passed to api method
        """

        next_page_url = urllib.parse.urljoin(endpoint, f"?cursorId={next_cursor_id}") if next_cursor_id is not None else endpoint
        page = api_method(next_page_url, **kwargs)
        for item in page.data:
            yield item

        if page.metadata.next_cursor_id is not None:
            yield from self._paginate(api_method, endpoint, page.metadata.next_cursor_id, **kwargs)
