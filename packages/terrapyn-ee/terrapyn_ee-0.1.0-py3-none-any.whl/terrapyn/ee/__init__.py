import importlib.metadata

from . import auth

__version__ = importlib.metadata.version("terrapyn.ee")

__all__ = ["auth"]

# Check if Earth Engine modules are available
if auth.check_ee_authentication():
	from . import data, io, stats, timeseries, utils

	__all__ = ["io", "stats", "utils", "data", "timeseries", "auth"]
