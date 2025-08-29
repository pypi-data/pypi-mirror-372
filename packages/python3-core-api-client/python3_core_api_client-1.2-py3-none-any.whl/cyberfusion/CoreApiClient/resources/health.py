from cyberfusion.CoreApiClient import models

from cyberfusion.CoreApiClient.interfaces import Resource


class Health(Resource):
    def read_health(
        self,
    ) -> models.HealthResource:
        return models.HealthResource.parse_obj(
            self.api_connector.send_or_fail(
                "GET", "/api/v1/health", data=None, query_parameters={}
            ).json
        )
