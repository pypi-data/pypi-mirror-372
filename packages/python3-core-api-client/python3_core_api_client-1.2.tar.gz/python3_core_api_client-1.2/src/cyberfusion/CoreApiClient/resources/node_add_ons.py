from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class NodeAddOns(Resource):
    def create_node_add_on(
        self,
        request: models.NodeAddOnCreateRequest,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/node-add-ons",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_node_add_ons(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.NodeAddOnResource]:
        return [
            models.NodeAddOnResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/node-add-ons",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def get_node_add_on_products(
        self,
    ) -> list[models.NodeAddOnProduct]:
        return [
            models.NodeAddOnProduct.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET", "/api/v1/node-add-ons/products", data=None, query_parameters={}
            ).json
        ]

    def read_node_add_on(
        self,
        *,
        id_: int,
    ) -> models.NodeAddOnResource:
        return models.NodeAddOnResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/node-add-ons/{id_}", data=None, query_parameters={}
            ).json
        )

    def delete_node_add_on(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE", f"/api/v1/node-add-ons/{id_}", data=None, query_parameters={}
            ).json
        )
