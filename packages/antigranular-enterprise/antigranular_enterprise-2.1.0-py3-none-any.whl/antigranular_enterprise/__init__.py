"""
Antigranular client package
"""


from .client import login
from .client import read_config
from .client import write_config
from .client import load_config
from .sql_client import login_sql
# Package version dunder
__version__ = "2.1.0"

# Package author dunder
__author__ = "Oblivious Software Pvt. Ltd."

# Package * imports dunder
__all__ = ["login", "login_sql", "read_config", "write_config", "load_config", "__version__", "__author__"]

# Read default config on import
# try:
#     read_config()
# except Exception:
#     pass # Ignore if config file is not found