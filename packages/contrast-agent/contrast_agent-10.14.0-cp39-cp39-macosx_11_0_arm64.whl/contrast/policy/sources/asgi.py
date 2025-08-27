# Copyright © 2025 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.policy.registry import register_source_nodes
from contrast.agent.policy.utils import CompositeNode


asgi_sources = [
    {
        "module": "starlette.requests",
        "class_name": "Request",
        "method_name": "body",
        "node_type": "BODY",
        "tags": ["CROSS_SITE"],
    },
    CompositeNode(
        {
            "module": "starlette.datastructures",
            "class_name": "FormData",
        },
        [
            {
                # We need get in addition to __getitem__, because starlette overrides them
                # both, and one doesn't call the other.
                "method_name": ["__getitem__", "get"],
                # MULTIPART_FORM_DATA isn't totally accurate, because forms could use
                # other content types
                "node_type": "MULTIPART_FORM_DATA",
                "tags": ["CROSS_SITE"],
            },
        ],
    ),
    CompositeNode(
        {
            "module": "aiohttp.web_request",
            "class_name": "BaseRequest",
        },
        [
            {
                "method_name": ["read", "json", "post"],
                "node_type": "BODY",
                "tags": ["CROSS_SITE"],
            },
        ],
    ),
    {
        "module": "aiohttp.multipart",
        "class_name": "BodyPartReader",
        "method_name": "read",
        "node_type": "MULTIPART_FORM_DATA",
        "tags": ["CROSS_SITE"],
    },
]


register_source_nodes(asgi_sources)
