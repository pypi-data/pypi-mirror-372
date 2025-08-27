"""
Work in progress.
"""

__version__: str
__version_tuple__: tuple
try:
    from assman._version import __version__, __version_tuple__  # pyright: ignore[reportMissingImports]
except ModuleNotFoundError:
    __version__ = '?'
    __version_tuple__ = (0, 0, 0, '?')
