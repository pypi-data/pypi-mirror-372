"""Initializes the shapefileexporter package.

This module exposes the primary interfaces for working with shapefile data,
including validation and export functionality. It provides access to:

- ShapeFileToDB: Class for validating and exporting shapefiles.
- StateShapeFileToDB: Class for exporting shapefiles by state.
- export_shapefile_to_db: Core function for exporting shapefile data to SQLite.

Typical usage example:
    from shapefileexporter import ShapeFileToDB, export_shapefile_to_db
"""

__version__ = "0.1.2"

from shapefile2db.shape_file_exporter import ShapeFileToDB
from shapefile2db.state_shape_file_exporter import StateShapeFileToDB
from shapefile2db.core import export_shapefile_to_db