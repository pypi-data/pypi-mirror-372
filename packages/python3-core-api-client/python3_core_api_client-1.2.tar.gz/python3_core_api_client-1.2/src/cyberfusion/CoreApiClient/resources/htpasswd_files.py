from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class HtpasswdFiles(Resource):
    def create_htpasswd_file(
        self,
        request: models.HtpasswdFileCreateRequest,
    ) -> models.HtpasswdFileResource:
        return models.HtpasswdFileResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/htpasswd-files",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_htpasswd_files(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.HtpasswdFileResource]:
        return [
            models.HtpasswdFileResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/htpasswd-files",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_htpasswd_file(
        self,
        *,
        id_: int,
    ) -> models.HtpasswdFileResource:
        return models.HtpasswdFileResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/htpasswd-files/{id_}", data=None, query_parameters={}
            ).json
        )

    def delete_htpasswd_file(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE",
                f"/api/v1/htpasswd-files/{id_}",
                data=None,
                query_parameters={},
            ).json
        )
