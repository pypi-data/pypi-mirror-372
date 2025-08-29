import sys

if sys.platform.startswith("win"):
    raise ImportError(
        "simcalibration requires rpy2, which is not supported in Windows."
        "Please use Linux or MacOS (or emulate a Unix environment with VirtualBox in Windows)"
    )

__version__ = "0.1.1"
