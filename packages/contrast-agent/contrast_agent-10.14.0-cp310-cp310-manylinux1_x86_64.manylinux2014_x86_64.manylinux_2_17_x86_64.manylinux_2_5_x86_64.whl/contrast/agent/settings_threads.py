# Copyright © 2025 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import threading
from abc import ABC, abstractmethod
from contrast.agent import scope
from contrast.agent.settings import Settings
from contrast.reporting.teamserver_messages import ServerActivity
from contrast.reporting.teamserver_messages.application_settings import (
    ApplicationSettings,
)
from contrast.utils.decorators import fail_loudly
from contrast.utils.timer import sleep
from contrast_vendor import structlog as logging

logger = logging.getLogger("contrast")
SERVER_SETTINGS_THREAD_NAME = "ContrastServerSettings"
APPLICATION_SETTINGS_THREAD_NAME = "ContrastApplicationSettings"
MIN_INTERVAL_MS = 10_000


class BaseSettingsThread(ABC, threading.Thread):
    def __init__(self, reporting_client, interval_ms: int, thread_name):
        self.stopped = False
        # Agent should not ping too frequently
        self.settings_interval_ms = max(interval_ms, MIN_INTERVAL_MS)
        self.reporting_client = reporting_client

        super().__init__()
        # A thread must have had __init__ called, but not start, to set daemon
        self.daemon = True
        self.name = thread_name

    def start(self):
        self.stopped = False
        super().start()

    @property
    def settings_interval_sec(self):
        return self.settings_interval_ms / 1000

    def run(self):
        # Ensure the polling thread runs in scope because it is
        # initialized before our thread.start patch is applied.
        with scope.contrast_scope():
            logger.debug("Starting settings polling thread", name=self.name)
            while not self.stopped and Settings().is_agent_config_enabled():
                self.send_settings()
                sleep(self.settings_interval_sec)

    @abstractmethod
    def send_settings(self) -> None: ...


class ServerSettingsThread(BaseSettingsThread):
    def __init__(self, reporting_client):
        super().__init__(
            reporting_client,
            Settings().config.server_settings_poll_interval,
            SERVER_SETTINGS_THREAD_NAME,
        )

    @fail_loudly("Error sending a server settings message")
    def send_settings(self):
        """
        We're currently hitting the Server Activity endpoint to get our server
        features/ settings. This NG style endpoint will eventually be replaced
        with the true v1 Server Settings endpoint, so naming around it reflects
        that. The Server Activity message is always empty, so we're already
        only using it for settings, not reporting. The content of the message
        is for now deprecated java-only features.
        """
        if Settings().config is None:
            return
        msg = ServerActivity()
        response = self.reporting_client.send_message(msg)
        msg.process_response(response, self.reporting_client)


class ApplicationSettingsThread(BaseSettingsThread):
    def __init__(self, reporting_client):
        super().__init__(
            reporting_client,
            Settings().config.application_settings_poll_interval,
            APPLICATION_SETTINGS_THREAD_NAME,
        )

    @fail_loudly("Error sending an application settings message")
    def send_settings(self):
        if Settings().config is None:
            return
        msg = ApplicationSettings()
        response = self.reporting_client.send_message(msg)
        msg.process_response(response, self.reporting_client)
