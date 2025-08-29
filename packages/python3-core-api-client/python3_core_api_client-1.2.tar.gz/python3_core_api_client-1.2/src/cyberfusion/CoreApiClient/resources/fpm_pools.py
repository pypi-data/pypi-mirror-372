from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class FPMPools(Resource):
    def create_fpm_pool(
        self,
        request: models.FPMPoolCreateRequest,
    ) -> models.FPMPoolResource:
        return models.FPMPoolResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/fpm-pools",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_fpm_pools(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.FPMPoolResource]:
        return [
            models.FPMPoolResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/fpm-pools",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_fpm_pool(
        self,
        *,
        id_: int,
    ) -> models.FPMPoolResource:
        return models.FPMPoolResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/fpm-pools/{id_}", data=None, query_parameters={}
            ).json
        )

    def update_fpm_pool(
        self,
        request: models.FPMPoolUpdateRequest,
        *,
        id_: int,
    ) -> models.FPMPoolResource:
        return models.FPMPoolResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/fpm-pools/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_fpm_pool(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE", f"/api/v1/fpm-pools/{id_}", data=None, query_parameters={}
            ).json
        )

    def restart_fpm_pool(
        self,
        *,
        id_: int,
        callback_url: Optional[str] = None,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/fpm-pools/{id_}/restart",
                data=None,
                query_parameters={
                    "callback_url": callback_url,
                },
            ).json
        )

    def reload_fpm_pool(
        self,
        *,
        id_: int,
        callback_url: Optional[str] = None,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/fpm-pools/{id_}/reload",
                data=None,
                query_parameters={
                    "callback_url": callback_url,
                },
            ).json
        )
