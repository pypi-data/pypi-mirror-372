# Copyright © 2025 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.protect.rule.base_rule import BaseRule
from contrast.agent.protect.rule.mode import Mode


class Xss(BaseRule):
    """
    Cross Site Scripting Protection rule
    Currently only a prefilter / block at perimeter rule
    """

    RULE_NAME = "reflected-xss"

    def is_prefilter(self):
        return self.enabled

    @property
    def mode(self):
        """
        Always block at perimeter
        """
        mode = self.settings.config.get(self.config_rule_path_mode)

        return Mode.BLOCK_AT_PERIMETER if mode == Mode.BLOCK else mode
