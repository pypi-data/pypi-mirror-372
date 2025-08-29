from typing import Annotated

import typer

PARALLEL_MIGRATION_TYPE = Annotated[
    int, typer.Option('--parallel', '-p', show_default=True, help='Sets how many migrations should be run in parallel')
]
PARALLEL_MIGRATION_DEFAULT = 4
