"""
ZCTA Shapefile Exporter

Exports ZIP Code Tabulation Area (ZCTA) geometries from a shapefile to a SQLite database.

Overview:
    - If a state is provided, only ZCTAs from that state are exported.
    - If no state is provided, all ZCTAs are exported.

This module is designed to work with shapefiles derived from the 2020 ZCTA dataset
provided by the US Census Bureau.

To download the official shapefiles, visit:
https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-files.2020.html
"""


from shapefile2db.shape_file_exporter import ShapeFileToDB
from shapefile2db.state_shape_file_exporter import StateShapeFileToDB 
from printpop import print_bold, print_red, print_green


def export_shapefile_to_db(state: str = None, shape_file_name: str = None, database_name: str = None):
    """Exports ZIP code geometries from a shapefile to a SQLite database.

    This function handles both state-specific and all-state exports based on the
    provided parameters. If a state is specified, it uses the StateShapeFileToDB
    class to filter and export ZIP code geometries for that state. If no state is
    specified, it uses the ShapeFileToDB class to export all ZIP code geometries.

    Args:
        state (str, optional): Two-letter abbreviation of the state (e.g., 'CA', 'TX').
                               If None, exports all states.
        shape_file_name (str, optional): Path to the .shp file. If None, uses default.
        database_name (str, optional): Name of the SQLite database. If None, uses default.

    Raises:
        ValueError: If the provided state is not a valid abbreviation in STATE_ZIP_RANGES.
    """
    if state:
        # Use StateShapeFileToDB for state-specific export
        exporter = StateShapeFileToDB(state=state, shape_file_name=shape_file_name, database_name=database_name)
    else:
        # Use ShapeFileToDB for all-state export
        exporter = ShapeFileToDB(shape_file_name=shape_file_name, database_name=database_name)

    # Get DataFrame from shapefile
    df = exporter.get_df_from_shapefile()
    
    # Export DataFrame to database
    exporter.export_shapedf_to_db(zcta_df=df)   


