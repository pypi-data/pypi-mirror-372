from cyberfusion.CoreApiClient import models
from typing import Optional

from cyberfusion.CoreApiClient.interfaces import Resource


class TaskCollections(Resource):
    def list_task_collection_results(
        self,
        *,
        uuid: str,
    ) -> list[models.TaskResult]:
        return [
            models.TaskResult.parse_obj(model)
            for model in self.api_connector.send_or_fail(
                "GET",
                f"/api/v1/task-collections/{uuid}/results",
                data=None,
                query_parameters={},
            ).json
        ]

    def retry_task_collection(
        self,
        *,
        uuid: str,
        callback_url: Optional[str] = None,
    ) -> models.TaskCollectionResource:
        return models.TaskCollectionResource.parse_obj(
            self.api_connector.send_or_fail(
                "POST",
                f"/api/v1/task-collections/{uuid}/retry",
                data=None,
                query_parameters={
                    "callback_url": callback_url,
                },
            ).json
        )
