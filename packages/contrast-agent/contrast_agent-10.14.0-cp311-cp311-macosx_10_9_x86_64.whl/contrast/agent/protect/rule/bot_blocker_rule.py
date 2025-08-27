# Copyright © 2025 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.protect.rule.base_rule import BaseRule


class BotBlocker(BaseRule):
    RULE_NAME = "bot-blocker"

    def is_prefilter(self):
        return self.enabled
