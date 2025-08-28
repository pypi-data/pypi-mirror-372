from test_culture_client.endpoints import TMS_PLUGIN_API_PREFIX, EndpointTemplate
from test_culture_client.models.folder import (
    CreateFolderRequest,
    MoveFolderRequest,
    RenameFolderRequest,
)


class Paths:
    # POST Создание папки
    CREATE = "%s/folder/create" % TMS_PLUGIN_API_PREFIX
    # POST Перемещение папки
    MOVE = "%s/folder/move" % TMS_PLUGIN_API_PREFIX
    # POST Изменение папки
    RENAME = "%s/folder/rename" % TMS_PLUGIN_API_PREFIX


class FolderEndpoint(EndpointTemplate):

    def create(self, json: CreateFolderRequest) -> dict:
        return self._client.post(Paths.CREATE, json=json)

    def move(self, json: MoveFolderRequest) -> dict:
        return self._client.post(Paths.MOVE, json=json)

    def rename(self, json: RenameFolderRequest) -> dict:
        return self._client.post(Paths.RENAME, json=json)
