from pathlib import Path

from kash.exec import import_and_register

import_and_register(
    __package__,
    Path(__file__).parent,
    [
        "actions",
        "analysis",
        "concepts",
        "doc_formats",
        "wiki",
        "links",
        "utils",
        "wiki",
    ],
)
