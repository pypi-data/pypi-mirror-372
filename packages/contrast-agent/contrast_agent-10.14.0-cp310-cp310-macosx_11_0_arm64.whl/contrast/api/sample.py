# Copyright © 2025 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from dataclasses import dataclass, field
from contrast.api.user_input import UserInput
from contrast.utils.timer import now_ms


@dataclass
class Sample:
    user_input: UserInput
    stack: list
    details: dict = field(default_factory=dict)
    timestamp_ms: int = field(default_factory=now_ms)
