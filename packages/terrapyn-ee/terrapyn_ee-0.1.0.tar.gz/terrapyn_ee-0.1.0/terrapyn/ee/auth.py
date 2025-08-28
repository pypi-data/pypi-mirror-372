import warnings


def check_ee_authentication() -> bool:
	"""
	Check if Earth Engine is properly authenticated and initialized.

	Returns:
		bool: True if EE is authenticated and ready to use, False otherwise
	"""
	try:
		import ee

		ee.Initialize()
		return True

	except ImportError:
		warnings.warn("Earth Engine Python library (earthengine-api) is not installed.", ImportWarning, stacklevel=2)
		return False

	except Exception as e:
		warnings.warn(f"Earth Engine authentication check failed: {str(e)}", UserWarning, stacklevel=2)
		return False
