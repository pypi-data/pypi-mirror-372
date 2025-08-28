from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version('django-ext')
except PackageNotFoundError:
    pass
