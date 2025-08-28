from typing import Annotated

import typer

from plus_sync.config import Config


def get_hashed_default() -> bool:
    config = Config.from_cmdargs()
    return config.hash_subject_ids


HashSubjectIDs = Annotated[
    bool,
    typer.Option(
        help='Whether to hash the subject IDs. Overrides the `hash_subject_ids` setting.',
        default_factory=get_hashed_default,
        show_default=False,
    ),
]
