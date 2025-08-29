from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class RootSSHKeys(Resource):
    def create_public_root_ssh_key(
        self,
        request: models.RootSSHKeyCreatePublicRequest,
    ) -> models.RootSSHKeyResource:
        return models.RootSSHKeyResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/root-ssh-keys/public",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def create_private_root_ssh_key(
        self,
        request: models.RootSSHKeyCreatePrivateRequest,
    ) -> models.RootSSHKeyResource:
        return models.RootSSHKeyResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/root-ssh-keys/private",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_root_ssh_keys(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.RootSSHKeyResource]:
        return [
            models.RootSSHKeyResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/root-ssh-keys",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_root_ssh_key(
        self,
        *,
        id_: int,
    ) -> models.RootSSHKeyResource:
        return models.RootSSHKeyResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/root-ssh-keys/{id_}", data=None, query_parameters={}
            ).json
        )

    def delete_root_ssh_key(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE", f"/api/v1/root-ssh-keys/{id_}", data=None, query_parameters={}
            ).json
        )
