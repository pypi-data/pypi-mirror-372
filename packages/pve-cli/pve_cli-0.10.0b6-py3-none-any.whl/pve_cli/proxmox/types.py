from typing import TypedDict


class ExecStatus(TypedDict):
    exitcode: int
    out_data: str
