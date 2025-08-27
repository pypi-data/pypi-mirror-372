# Copyright © 2025 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import json

from contrast.agent.protect.rule.nosql_injection.mongo_nosql_scanner import (
    MongoNoSqlScanner,
)
from contrast.agent.protect.rule.sqli_rule import SqlInjection
from contrast.utils.decorators import fail_quietly


class NoSqlInjection(SqlInjection):
    """
    NoSQL Injection Protection rule
    """

    RULE_NAME = "nosql-injection"

    def get_database_scanner(self, database):
        return MongoNoSqlScanner()

    def skip_protect_analysis(self, user_input, args, kwargs):
        """
        nosql-injection has many potential user input types so
        let's not skip analysis
        """
        return False

    def convert_input(self, user_input):
        if not isinstance(user_input, (str, bytes)):
            user_input = obj_to_str(user_input)

        return super().convert_input(user_input)


@fail_quietly("Failed to convert nosql obj input to str", return_value="")
def obj_to_str(obj):
    """
    Convert one of the common obj types passed to pymongo methods into a string.

    :param obj: list, dict, bson or a type that inherits from collections.MutableMapping
    :return: str
    """
    try:
        return json.dumps(obj)
    except TypeError:
        # may encounter TypeError: Object of type ObjectId is not JSON serializable
        # so let's just make it a string
        return str(obj)
