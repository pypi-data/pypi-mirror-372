from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource


class MailAccounts(Resource):
    def create_mail_account(
        self,
        request: models.MailAccountCreateRequest,
    ) -> models.MailAccountResource:
        return models.MailAccountResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                "/api/v1/mail-accounts",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def list_mail_accounts(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> list[models.MailAccountResource]:
        return [
            models.MailAccountResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                "/api/v1/mail-accounts",
                data=None,
                query_parameters={
                    "skip": skip,
                    "limit": limit,
                    "filter": filter_,
                    "sort": sort,
                },
            ).json
        ]

    def read_mail_account(
        self,
        *,
        id_: int,
    ) -> models.MailAccountResource:
        return models.MailAccountResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", f"/api/v1/mail-accounts/{id_}", data=None, query_parameters={}
            ).json
        )

    def update_mail_account(
        self,
        request: models.MailAccountUpdateRequest,
        *,
        id_: int,
    ) -> models.MailAccountResource:
        return models.MailAccountResource.parse_obj(
            self.api_connector.send_or_fail(
                "PATCH",
                f"/api/v1/mail-accounts/{id_}",
                data=request.dict(exclude_unset=True),
                query_parameters={},
            ).json
        )

    def delete_mail_account(
        self,
        *,
        id_: int,
        delete_on_cluster: Optional[bool] = None,
    ) -> models.DetailMessage:
        return models.DetailMessage.parse_obj(
            self.api_connector.send_or_fail(
                "DELETE",
                f"/api/v1/mail-accounts/{id_}",
                data=None,
                query_parameters={
                    "delete_on_cluster": delete_on_cluster,
                },
            ).json
        )

    def list_mail_account_usages(
        self,
        *,
        mail_account_id: int,
        timestamp: str,
        time_unit: Optional[models.MailAccountUsageResource] = None,
    ) -> list[models.MailAccountUsageResource]:
        return [
            models.MailAccountUsageResource.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/mail-accounts/usages/{mail_account_id}",
                data=None,
                query_parameters={
                    "timestamp": timestamp,
                    "time_unit": time_unit,
                },
            ).json
        ]
