from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("remotivelabs-broker")
except PackageNotFoundError:
    __version__ = "unknown"
