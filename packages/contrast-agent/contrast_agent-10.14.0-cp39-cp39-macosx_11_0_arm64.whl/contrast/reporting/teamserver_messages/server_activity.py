# Copyright © 2025 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import requests

from .base_ts_message import BaseTsServerMessage
from .effective_config import EffectiveConfig
from contrast.utils.decorators import fail_loudly
from contrast.utils.timer import now_ms


class ServerActivity(BaseTsServerMessage):
    def __init__(self):
        super().__init__()

        # NOTE: When we eventually use ServerSettings here, we'll need to use
        # `If-Modified-Since` / datetime logic. See ApplicationSettings.
        self.body = {"lastUpdate": self.since_last_update}

    @property
    def name(self):
        return "server-activity"

    @property
    def path(self):
        return "activity/server"

    @property
    def request_method(self):
        return requests.put

    @property
    def expected_response_codes(self):
        return [200, 304]

    @property
    def since_last_update(self):
        """
        Time in ms since server have been updated.
        If never updated, then it's been 0ms since then.
        """
        if self.settings.last_server_update_time_ms == 0:
            return 0
        return now_ms() - self.settings.last_server_update_time_ms

    @fail_loudly("Failed to process ServerActivity response")
    def process_response(self, response, reporting_client):
        super().process_response(response, reporting_client)

        if not self.process_response_code(response, reporting_client):
            return

        self.settings.log_effective_config()
        if (
            reporting_client is not None
            and self.settings.is_agent_config_enabled()
            # This is necessary to ensure the application exists in TeamServer
            and self.settings.config.session_id != ""
        ):
            reporting_client.add_message(EffectiveConfig())
