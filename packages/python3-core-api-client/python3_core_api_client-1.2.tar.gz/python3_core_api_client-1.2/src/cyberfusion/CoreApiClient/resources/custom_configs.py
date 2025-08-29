from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class CustomConfigs(Resource):
    def create_custom_config(
        self,
        request: models.CustomConfigCreateRequest,
    ) -> models.CustomConfigResource:
        return models.CustomConfigResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/custom-configs",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_custom_configs(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.CustomConfigResource]:
        return [
            models.CustomConfigResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/custom-configs",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_custom_config(
        self,
        *,
        id_: int,
    ) -> models.CustomConfigResource:
        return models.CustomConfigResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/custom-configs/{id_}", data=None, query_parameters={}
            ).json
        )

    def update_custom_config(
        self,
        request: models.CustomConfigUpdateRequest,
        *,
        id_: int,
    ) -> models.CustomConfigResource:
        return models.CustomConfigResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/custom-configs/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_custom_config(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE",
                f"/api/v1/custom-configs/{id_}",
                data=None,
                query_parameters={},
            ).json
        )
