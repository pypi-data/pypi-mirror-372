from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class RedisInstances(Resource):
    def create_redis_instance(
        self,
        request: models.RedisInstanceCreateRequest,
    ) -> models.RedisInstanceResource:
        return models.RedisInstanceResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/redis-instances",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_redis_instances(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.RedisInstanceResource]:
        return [
            models.RedisInstanceResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/redis-instances",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_redis_instance(
        self,
        *,
        id_: int,
    ) -> models.RedisInstanceResource:
        return models.RedisInstanceResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/redis-instances/{id_}", data=None, query_parameters={}
            ).json
        )

    def update_redis_instance(
        self,
        request: models.RedisInstanceUpdateRequest,
        *,
        id_: int,
    ) -> models.RedisInstanceResource:
        return models.RedisInstanceResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/redis-instances/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_redis_instance(
        self,
        *,
        id_: int,
        delete_on_cluster: Optional[bool] = None,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE",
                f"/api/v1/redis-instances/{id_}",
                data=None,
                query_parameters={
                    "delete_on_cluster": delete_on_cluster,
                },
            ).json
        )
