from collections.abc import Callable


def throws_exception(func: Callable[..., any], exception_type: type[Exception] = Exception) -> bool:
    def wrapped(*args: list[any], **kwargs: dict[str, any]):
        try:
            func(*args, **kwargs)
            return False  # noqa: TRY300
        except exception_type:
            return True

    return wrapped
