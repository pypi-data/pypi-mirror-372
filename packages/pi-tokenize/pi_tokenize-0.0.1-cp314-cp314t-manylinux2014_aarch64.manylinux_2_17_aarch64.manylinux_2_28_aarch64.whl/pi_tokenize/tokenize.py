from ._vendor.cpython.tokenize import *  # noqa: F403


from ._vendor.cpython import tokenize as __tokenize

__all__ = __tokenize.__all__  # pyright: ignore[reportUnsupportedDunderAll]
