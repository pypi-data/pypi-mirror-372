from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class HtpasswdUsers(Resource):
    def create_htpasswd_user(
        self,
        request: models.HtpasswdUserCreateRequest,
    ) -> models.HtpasswdUserResource:
        return models.HtpasswdUserResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/htpasswd-users",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_htpasswd_users(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.HtpasswdUserResource]:
        return [
            models.HtpasswdUserResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/htpasswd-users",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_htpasswd_user(
        self,
        *,
        id_: int,
    ) -> models.HtpasswdUserResource:
        return models.HtpasswdUserResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/htpasswd-users/{id_}", data=None, query_parameters={}
            ).json
        )

    def update_htpasswd_user(
        self,
        request: models.HtpasswdUserUpdateRequest,
        *,
        id_: int,
    ) -> models.HtpasswdUserResource:
        return models.HtpasswdUserResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/htpasswd-users/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_htpasswd_user(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE",
                f"/api/v1/htpasswd-users/{id_}",
                data=None,
                query_parameters={},
            ).json
        )
