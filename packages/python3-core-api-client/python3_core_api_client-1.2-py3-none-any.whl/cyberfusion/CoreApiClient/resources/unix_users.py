from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class UNIXUsers(Resource):
    def create_unix_user(
        self,
        request: models.UNIXUserCreateRequest,
    ) -> models.UNIXUserResource:
        return models.UNIXUserResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/unix-users",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_unix_users(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.UNIXUserResource]:
        return [
            models.UNIXUserResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/unix-users",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_unix_user(
        self,
        *,
        id_: int,
    ) -> models.UNIXUserResource:
        return models.UNIXUserResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/unix-users/{id_}", data=None, query_parameters={}
            ).json
        )

    def update_unix_user(
        self,
        request: models.UNIXUserUpdateRequest,
        *,
        id_: int,
    ) -> models.UNIXUserResource:
        return models.UNIXUserResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/unix-users/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_unix_user(
        self,
        *,
        id_: int,
        delete_on_cluster: Optional[bool] = None,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE",
                f"/api/v1/unix-users/{id_}",
                data=None,
                query_parameters={
                    "delete_on_cluster": delete_on_cluster,
                },
            ).json
        )

    def compare_unix_users(
        self,
        *,
        left_unix_user_id: int,
        right_unix_user_id: int,
    ) -> models.UNIXUserComparison:
        return models.UNIXUserComparison.parse_obj(
            self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/unix-users/{left_unix_user_id}/comparison",
                data=None,
                query_parameters={
                    "right_unix_user_id": right_unix_user_id,
                },
            ).json
        )

    def list_unix_user_usages(
        self,
        *,
        unix_user_id: int,
        timestamp: str,
        time_unit: Optional[models.UNIXUserUsageResource] = None,
    ) -> list[models.UNIXUserUsageResource]:
        return [
            models.UNIXUserUsageResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/unix-users/usages/{unix_user_id}",
                data=None,
                query_parameters={
                    "timestamp": timestamp,
                    "time_unit": time_unit,
                },
            ).json
        ]
