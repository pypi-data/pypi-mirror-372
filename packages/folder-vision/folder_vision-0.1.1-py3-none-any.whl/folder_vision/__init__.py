from importlib import metadata as _metadata

try:
	__version__ = _metadata.version("folder-vision")
except _metadata.PackageNotFoundError:  # pragma: no cover
	__version__ = "0.0.0+local"

from .app import app  # noqa: E402

__all__ = ["app", "__version__"]
