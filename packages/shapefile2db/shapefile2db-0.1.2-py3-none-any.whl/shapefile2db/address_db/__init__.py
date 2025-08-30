# address_db/__init__.py
# 
# """
# Manages connection and initialization of the address.db file
# """

__version__ = "0.1.2"

from shapefile2db.address_db.address_database import AddressDatabase
from shapefile2db.address_db.address_constants import STATE_DICT, STATE_ZIP_RANGES
