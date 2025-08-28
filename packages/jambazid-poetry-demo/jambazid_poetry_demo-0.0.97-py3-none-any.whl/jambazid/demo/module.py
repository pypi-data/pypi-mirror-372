"""
Sample module file.

See https://google.github.io/styleguide/pyguide.html for example style.
"""

import typing

from jambazid.demo import subpackage

# CONSTANTS:


A_CONSTANT: str = subpackage.__file__


# MAIN:


def main() -> None:
    """
    Summarise the business logic.
    """
    assert is_boolean(False)
    assert is_str("hello")
    assert get_result_by_magic(1, ("1",), 0.1, None)


# HELPERS:


def is_boolean(value: typing.Any, /) -> bool:
    # Docstring is redundant here - good naming + type hints are enough.
    return isinstance(value, bool)


def is_str(value: typing.Any, /) -> bool:
    # Docstring is redundant here - good naming + type hints are enough.
    return isinstance(value, str)


def get_result_by_magic(
    arg_1: int,
    arg_2: tuple[str, ...],
    *args: float | set[str] | None,
    **kwargs: typing.Mapping[str, typing.Sequence[int]] | typing.Generator[int, None, bool],
) -> bool:
    """
    A complex function that needs documenting.

    Args:
        arg_1:
            lorem ipsum.
        arg_2:
            lorem ipsum.
        *args:
            If a `float` is supplied then ...
        **kwargs:
            If a `Mapping` is supplied then ...
            If a `Generator` is supplied then ...

    Returns:
        A `bool` flagging ... lorem ipsum.

    Raises:
        ValueError: An invalid set of arguments was supplied.
    """
    matched: bool = str(arg_1) in arg_2
    if matched and any(i is None for i in args):
        return False
    elif matched := any(isinstance(v, typing.Mapping) for v in kwargs.values()):
        return matched
    raise ValueError("Lorem ipsum.")


# ENTRYPOINT:


if __name__ == "__main__":
    main()
