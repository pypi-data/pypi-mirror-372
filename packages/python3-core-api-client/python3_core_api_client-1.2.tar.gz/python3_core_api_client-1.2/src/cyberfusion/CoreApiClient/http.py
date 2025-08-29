import json
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any

from requests.structures import CaseInsensitiveDict


@dataclass
class Response:
    status_code: int
    body: str
    headers: CaseInsensitiveDict

    @property
    def failed(self) -> bool:
        return self.status_code >= HTTPStatus.BAD_REQUEST

    @property
    def json(self) -> Any:
        return json.loads(self.body)
