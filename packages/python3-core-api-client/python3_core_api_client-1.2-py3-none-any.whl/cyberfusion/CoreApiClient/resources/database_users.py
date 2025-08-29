from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class DatabaseUsers(Resource):
    def create_database_user(
        self,
        request: models.DatabaseUserCreateRequest,
    ) -> models.DatabaseUserResource:
        return models.DatabaseUserResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/database-users",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_database_users(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.DatabaseUserResource]:
        return [
            models.DatabaseUserResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/database-users",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_database_user(
        self,
        *,
        id_: int,
    ) -> models.DatabaseUserResource:
        return models.DatabaseUserResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/database-users/{id_}", data=None, query_parameters={}
            ).json
        )

    def update_database_user(
        self,
        request: models.DatabaseUserUpdateRequest,
        *,
        id_: int,
    ) -> models.DatabaseUserResource:
        return models.DatabaseUserResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/database-users/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_database_user(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE",
                f"/api/v1/database-users/{id_}",
                data=None,
                query_parameters={},
            ).json
        )
