from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class MailDomains(Resource):
    def create_mail_domain(
        self,
        request: models.MailDomainCreateRequest,
    ) -> models.MailDomainResource:
        return models.MailDomainResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/mail-domains",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_mail_domains(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.MailDomainResource]:
        return [
            models.MailDomainResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/mail-domains",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_mail_domain(
        self,
        *,
        id_: int,
    ) -> models.MailDomainResource:
        return models.MailDomainResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/mail-domains/{id_}", data=None, query_parameters={}
            ).json
        )

    def update_mail_domain(
        self,
        request: models.MailDomainUpdateRequest,
        *,
        id_: int,
    ) -> models.MailDomainResource:
        return models.MailDomainResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/mail-domains/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_mail_domain(
        self,
        *,
        id_: int,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE", f"/api/v1/mail-domains/{id_}", data=None, query_parameters={}
            ).json
        )
