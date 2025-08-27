# arpakit
import datetime as dt
from typing import Any

from pydantic import BaseModel, ConfigDict

from arpakitlib.ar_datetime_util import now_utc_dt

_ARPAKIT_LIB_MODULE_VERSION = "3.0"


class SafeFuncResult(BaseModel):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True, from_attributes=True)

    is_ok: bool = False
    func_result: Any = None
    exception: Exception | None = None
    duration: dt.timedelta | None = None


def sync_safely_run_func(*, sync_func, args: tuple | None = None, kwargs: dict | None = None) -> SafeFuncResult:
    if args is None:
        args = tuple()
    if kwargs is None:
        kwargs = {}
    func_start_dt = now_utc_dt()
    try:
        res = sync_func(*args, **kwargs)
        duration = now_utc_dt() - func_start_dt
        return SafeFuncResult(
            is_ok=True,
            func_result=res,
            duration=duration
        )
    except Exception as exception:
        return SafeFuncResult(
            is_ok=False,
            exception=exception
        )


def __example():
    def div(a: int, b: int) -> float:
        return a / b

    # успешный вызов
    ok_result = sync_safely_run_func(sync_func=div, args=(10, 2))
    print("OK result:", ok_result.model_dump())

    # вызов с исключением
    err_result = sync_safely_run_func(sync_func=div, args=(10, 0))
    print("ERR result:", err_result.model_dump())


if __name__ == "__main__":
    __example()
