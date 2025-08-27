# Copyright © 2025 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.

from contrast.agent import scope
from contrast_rewriter import rewrite_for_pytest
from contrast.agent.patch_controller import (
    enable_assess_patches,
    is_preinstrument_flag_set,
)
from contrast.agent.policy.rewriter import apply_rewrite_policy
from contrast.configuration.agent_config import AgentConfig
from contrast.patches import (
    register_chaining_monkeypatches,
    register_automatic_middleware_monkeypatches,
)


@scope.contrast_scope()
def apply_early_instrumentation():
    """
    Applies a subset of instrumentation during site loading.

    Currently, only instrumentation that needs to be applied as early as possible
    is applied here. Eventually, it would be simpler to apply all instrumentation,
    but that will require more refactoring.
    """

    if rewrite_for_pytest():
        apply_rewrite_policy()
        return

    preinstrument = is_preinstrument_flag_set()

    config = AgentConfig()

    # Policy-based rewrites need to be applied prior to any policy patches.
    # Policy patches can be layered on top of rewritten functions. So that
    # means we need to make sure that the "original" function called by the
    # policy patch is the *rewritten* one.
    if config.assess_enabled or preinstrument:
        apply_rewrite_policy()

    if config.enable_automatic_middleware or preinstrument:
        register_automatic_middleware_monkeypatches()

    if config.assess_enabled or preinstrument:
        # NOTE: policy is currently loaded/generated on import. It is applied explicitly
        # in policy/applicator.py later
        from contrast import policy  # noqa: F401

        enable_assess_patches()

    register_chaining_monkeypatches()
