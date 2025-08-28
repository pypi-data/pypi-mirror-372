from ._vendor.cpython.token import *  # noqa: F403


from ._vendor.cpython import token as __token

__all__ = __token.__all__  # pyright: ignore[reportUnsupportedDunderAll]
