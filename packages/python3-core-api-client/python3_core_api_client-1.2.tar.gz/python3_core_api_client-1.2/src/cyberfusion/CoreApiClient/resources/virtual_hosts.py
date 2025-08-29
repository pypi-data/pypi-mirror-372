from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class VirtualHosts(Resource):
    def create_virtual_host(
        self,
        request: models.VirtualHostCreateRequest,
    ) -> models.VirtualHostResource:
        return models.VirtualHostResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/virtual-hosts",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_virtual_hosts(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.VirtualHostResource]:
        return [
            models.VirtualHostResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/virtual-hosts",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_virtual_host(
        self,
        *,
        id_: int,
    ) -> models.VirtualHostResource:
        return models.VirtualHostResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/virtual-hosts/{id_}", data=None, query_parameters={}
            ).json
        )

    def update_virtual_host(
        self,
        request: models.VirtualHostUpdateRequest,
        *,
        id_: int,
    ) -> models.VirtualHostResource:
        return models.VirtualHostResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/virtual-hosts/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_virtual_host(
        self,
        *,
        id_: int,
        delete_on_cluster: Optional[bool] = None,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE",
                f"/api/v1/virtual-hosts/{id_}",
                data=None,
                query_parameters={
                    "delete_on_cluster": delete_on_cluster,
                },
            ).json
        )

    def get_virtual_host_document_root(
        self,
        *,
        id_: int,
    ) -> models.VirtualHostDocumentRoot:
        return models.VirtualHostDocumentRoot.parse_obj(
            self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/virtual-hosts/{id_}/document-root",
                data=None,
                query_parameters={},
            ).json
        )

    def sync_domain_roots_of_virtual_hosts(
        self,
        *,
        left_virtual_host_id: int,
        right_virtual_host_id: int,
        callback_url: Optional[str] = None,
        exclude_paths: Optional[List[str]] = None,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/virtual-hosts/{left_virtual_host_id}/domain-root/sync",
                data=None,
                query_parameters={
                    "callback_url": callback_url,
                    "right_virtual_host_id": right_virtual_host_id,
                    "exclude_paths": exclude_paths,
                },
            ).json
        )
