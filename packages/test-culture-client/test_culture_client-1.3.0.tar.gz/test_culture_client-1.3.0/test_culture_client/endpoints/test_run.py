from test_culture_client.endpoints import TMS_PLUGIN_API_PREFIX, EndpointTemplate
from test_culture_client.models.test_run import (
    CreateTestRunRequest,
    UpdateTestRunStatusRequest,
)


class Paths:
    UNIT_TYPE = "test_case_run"

    # PUT Создание прогона тест-кейса
    CREATE = "%s/run/create" % TMS_PLUGIN_API_PREFIX
    # POST Изменение статуса прогона тест-кейса
    CHANGE_STATUS = "%s/run/{unit_id}/status" % TMS_PLUGIN_API_PREFIX


class TestRunEndpoint(EndpointTemplate):

    def create(self, json: CreateTestRunRequest) -> dict:
        return self._client.post(Paths.CREATE, json=json)

    def update_status(self, unit_id: str, json: UpdateTestRunStatusRequest) -> dict:
        return self._client.patch(
            Paths.CHANGE_STATUS.format(unit_id=unit_id), json=json
        )
