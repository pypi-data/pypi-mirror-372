from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class FTPUsers(Resource):
    def create_ftp_user(
        self,
        request: models.FTPUserCreateRequest,
    ) -> models.FTPUserResource:
        return models.FTPUserResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/ftp-users",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_ftp_users(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.FTPUserResource]:
        return [
            models.FTPUserResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/ftp-users",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_ftp_user(
        self,
        *,
        id_: int,
    ) -> models.FTPUserResource:
        return models.FTPUserResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/ftp-users/{id_}", data=None, query_parameters={}
            ).json
        )

    def update_ftp_user(
        self,
        request: models.FTPUserUpdateRequest,
        *,
        id_: int,
    ) -> models.FTPUserResource:
        return models.FTPUserResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/ftp-users/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_ftp_user(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE", f"/api/v1/ftp-users/{id_}", data=None, query_parameters={}
            ).json
        )

    def create_temporary_ftp_user(
        self,
        request: models.TemporaryFTPUserCreateRequest,
    ) -> models.TemporaryFTPUserResource:
        return models.TemporaryFTPUserResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/ftp-users/temporary",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )
