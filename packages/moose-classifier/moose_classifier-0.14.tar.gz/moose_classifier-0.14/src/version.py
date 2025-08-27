from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version('moose-classifier')
except PackageNotFoundError:
    __version__ = ''
