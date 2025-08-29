from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class Customers(Resource):
    def list_customers(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.CustomerResource]:
        return [
            models.CustomerResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/customers",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_customer(
        self,
        *,
        id_: int,
    ) -> models.CustomerResource:
        return models.CustomerResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/customers/{id_}", data=None, query_parameters={}
            ).json
        )

    def list_ip_addresses_for_customer(
        self,
        *,
        id_: int,
    ) -> models.CustomerIPAddresses:
        return models.CustomerIPAddresses.parse_obj(
            self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/customers/{id_}/ip-addresses",
                data=None,
                query_parameters={},
            ).json
        )

    def create_ip_address_for_customer(
        self,
        request: models.CustomerIPAddressCreateRequest,
        *,
        id_: int,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/customers/{id_}/ip-addresses",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_ip_address_for_customer(
        self,
        *,
        id_: int,
        ip_address: str,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE",
                f"/api/v1/customers/{id_}/ip-addresses/{ip_address}",
                data=None,
                query_parameters={},
            ).json
        )

    def get_ip_addresses_products_for_customers(
        self,
    ) -> list[models.IPAddressProduct]:
        return [
            models.IPAddressProduct.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/customers/ip-addresses/products",
                data=None,
                query_parameters={},
            ).json
        ]
