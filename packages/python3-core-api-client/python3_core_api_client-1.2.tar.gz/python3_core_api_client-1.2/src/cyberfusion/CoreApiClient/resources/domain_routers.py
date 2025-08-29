from cyberfusion.CoreApiClient import models
from typing import Optional, List
from cyberfusion.CoreApiClient.interfaces import Resource


class DomainRouters(Resource):
    def list_domain_routers(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.DomainRouterResource]:
        return [
            models.DomainRouterResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/domain-routers",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def update_domain_router(
        self,
        request: models.DomainRouterUpdateRequest,
        *,
        id_: int,
    ) -> models.DomainRouterResource:
        return models.DomainRouterResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/domain-routers/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )
