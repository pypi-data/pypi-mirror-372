from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class Nodes(Resource):
    def create_node(
        self,
        request: models.NodeCreateRequest,
        *,
        callback_url: Optional[str] = None,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/nodes",
                data=request.dict(exclude_unset=True),
                query_parameters={
                    "callback_url": callback_url,
                },
            ).json
        )

    def list_nodes(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.NodeResource]:
        return [
            models.NodeResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/nodes",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def get_node_products(
        self,
    ) -> list[models.NodeProduct]:
        return [
            models.NodeProduct.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET", "/api/v1/nodes/products", data=None, query_parameters={}
            ).json
        ]

    def read_node(
        self,
        *,
        id_: int,
    ) -> models.NodeResource:
        return models.NodeResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/nodes/{id_}", data=None, query_parameters={}
            ).json
        )

    def update_node(
        self,
        request: models.NodeUpdateRequest,
        *,
        id_: int,
    ) -> models.NodeResource:
        return models.NodeResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/nodes/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_node(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE", f"/api/v1/nodes/{id_}", data=None, query_parameters={}
            ).json
        )

    def upgrade_downgrade_node(
        self,
        *,
        id_: int,
        callback_url: Optional[str] = None,
        product: str,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/nodes/{id_}/xgrade",
                data=None,
                query_parameters={
                    "callback_url": callback_url,
                    "product": product,
                },
            ).json
        )
