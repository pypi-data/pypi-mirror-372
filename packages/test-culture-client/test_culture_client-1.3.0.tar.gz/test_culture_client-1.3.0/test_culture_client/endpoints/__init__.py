TMS_PLUGIN_API_PREFIX = "/extension/plugin/v2/rest/api/swtr_tms_plugin/v1"

class EndpointTemplate:
    """Class with basic constructor for endpoint classes"""
    def __init__(self, client: "ApiClient"):
        self._client = client