# Copyright © 2025 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast import AGENT_CURR_WORKING_DIR
from contrast.agent.protect.rule.base_rule import BaseRule
from collections.abc import Iterable

from contrast.utils.decorators import fail_quietly

PARENT_CHECK = ".."
SLASH = "/"
SAFE_PATHS = ["tmp", "public", "docs", "static", "template", "templates"]
WRITE_OPTIONS = ["w", "a"]


class PathTraversal(BaseRule):
    RULE_NAME = "path-traversal"

    def build_sample(self, evaluation, path, **kwargs):
        sample = self.build_base_sample(evaluation)
        if path is not None:
            sample.details["path"] = path
        return sample

    @fail_quietly(
        "Failed to run path traversal skip_protect_analysis", return_value=False
    )
    def skip_protect_analysis(self, user_input, args, kwargs):
        write = possible_write(args, kwargs)
        if write:
            # any write is a risk so we should not skip analysis
            return False

        return not actionable_path(user_input)

    def infilter_kwargs(self, user_input, patch_policy):
        return dict(method=patch_policy.method_name)


def possible_write(args, kwargs):
    return _possible_write_kwargs(kwargs) or _possible_write_args(args)


def _possible_write_kwargs(kwargs):
    mode = kwargs.get("mode", "")

    if not isinstance(mode, (str, bytes)):
        return False

    return mode and any([x in mode for x in WRITE_OPTIONS])


def _possible_write_args(args):
    if not isinstance(args, Iterable):
        return False

    return (
        len(args) > 1
        and args[1] is not None
        and isinstance(args[1], Iterable)
        and any([x in args[1] for x in WRITE_OPTIONS])
    )


def actionable_path(path):
    if not path or not isinstance(path, str):
        return False

    # moving up directory structure is a risk and hence actionable
    if path.find(PARENT_CHECK) > 1:
        return True

    if "/contrast/" in path or "/site-packages/" in path:
        return False

    if path.startswith(SLASH):
        for prefix in _safer_abs_paths():
            if path.startswith(prefix):
                return False
    else:
        for prefix in SAFE_PATHS:
            if path.startswith(prefix):
                return False

    return True


def _safer_abs_paths():
    return (
        [f"{AGENT_CURR_WORKING_DIR}/{item}" for item in SAFE_PATHS]
        if AGENT_CURR_WORKING_DIR
        else []
    )
