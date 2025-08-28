from typing import TYPE_CHECKING

from layernext.datalake.keys import SELECTION_ID, USER_ID


if TYPE_CHECKING:
    from . import DatalakeClient


class FileTrash:
    def __init__(self, client: "DatalakeClient"):
        self._client = client

    def trash_files(self, selection_id, user_id="Python SDK"):
        payload = {SELECTION_ID: selection_id, USER_ID: user_id}

        response = self._client.datalake_interface.trash_files(payload)
        return response
