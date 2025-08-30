"""
ShapeFileToDB

Processes the 2020 ZCTA shapefile from the US Census Bureau and exports ZIP code
geometry data to a SQLite database.

Overview:
    This class filters ZIP code geometries based on valid classifications and stores
    ZIP codes, tabulation areas, and boundary points in a database. Boundary points
    can number in the thousands per ZIP code and are the primary driver of runtime.

Features:
    - Filters ZIP code geometries using classification rules.
    - Saves ZIP codes, tabulation areas, and boundary coordinates to SQLite.
    - Requires both .shp and .shx files for optimal performance.

Usage:
    - Set the shapefile path and database path via `__init__`, or use defaults.
    - Call `export()` to execute the export process.
    - Searches for shapefiles in the working directory or a specified relative path.
    - Exports all states by default. For single-state exports, use `StateShapeFileToDB`.

Author:
    Ryan LaPine

Date:
    2025-07-25

Version:
    0.1.2

Required Shapefile Components:
    .shp (Shape Format):
        Contains the primary geometry data for each feature (points, lines, polygons).

    .shx (Shape Index Format):
        Provides an index for efficient access to geometry records in the .shp file.

    .dbf (dBASE Table Format):
        Stores attribute data linked to each geometry, such as ZIP code and classification.

Note:
    All three files (.shp, .shx, .dbf) are required for full shapefile functionality.
    The .shx file significantly improves performance when accessing large geometries.
"""


# Standard library imports
import os  # For file path manipulation, environment variables, or directory operations
import threading  # For concurrent execution or background tasks
import time  # For delays, timing, or performance measurement
from datetime import datetime  # For timestamping, logging, or date-based filtering

# Third-party libraries
import pandas as pd  # For tabular data manipulation
import geopandas as gpd  # For geospatial data handling
from geopandas import GeoDataFrame  # Explicit import for type hinting or subclassing
import shapely.geometry  # For geometric operations (points, polygons, etc.)
from printpop import (
    print_red, print_cyan, print_lime, print_pink, print_orange, print_bold
)  # Styled console output for emphasis or debugging

# Fiona and Pyogrio: used for geospatial file I/O and error handling
from pyogrio.errors import DataSourceError  # Raised when reading geospatial files fails

# Project-specific modules
from shapefile2db.address_db.address_database import AddressDatabase  # Database interface for address-related operations


class ShapeFileToDB:
    """Handles reading a US Census shapefile and loading ZIP code data into a SQLite database."""

    # --- File and Database Configuration ---
    # DB_NAME = "shapefileexporter/data/address.db"
    DB_NAME = "address.db"
    # default is 2020 us census zcta shapefile
    SHAPE_FILE_NAME = "tl_2020_us_zcta520.shp"
    ZIP_LENGTH = 5

    # --- Table Names ---
    ZIP_TABLE = "zip_codes"
    ZCTA_TABLE = "zip_tabulation_areas"
    POINTS_TABLE = "zip_boundary_points"

    # --- ZIP Code Table Fields ---
    ZIP_ID_FIELD = "zip_code_id"
    ZIP_CODE_FIELD = "zip_code"
    ZIP_CODE_LAT_FIELD = "zip_lat"
    ZIP_CODE_LON_FIELD = "zip_lon"

    # --- ZCTA Table Fields ---
    ZCTA_ID_FIELD = "zip_tabulation_area_id"
    LAT_POINT_FIELD = "lat"
    LON_POINT_FIELD = "lon"

    # --- Census Shapefile Fields ---
    ZIP_FIELD = 'ZCTA5CE20'
    ZIP_GEOID_FIELD = 'GEOID20'
    ZIP_CLASS_FIELD = 'CLASSFP20'
    ZIP_FEATURE_FIELD = 'MTFCC20'
    ZIP_STATUS_FIELD = 'FUNCSTAT20'
    ZIP_LAND_AREA_FIELD = 'ALAND20'
    ZIP_WATER_AREA_FIELD = 'AWATER20'
    ZIP_LAT_FIELD = 'INTPTLAT20'
    ZIP_LON_FIELD = 'INTPTLON20'
    ZIP_GEOMETRY_FIELD = 'geometry'

    # --- Valid ZIP Area Criteria ---
    ZIP_FEATURE_CODE = "G6350"
    ZIP_CLASS = "B5"
    ZIP_STATUS = "S"

    # --- Runtime Configuration ---
    ROW_INCREMENT = 1000

    # --- UI Configuration ---
    LABEL_JUST = 20
    TIMER_JUST = 11

    # --- Instance Variables ---
    absolute_file_path = None  # Absolute path to the shapefile
    absolute_db_path = None    # Absolute path to the SQLite database

    timer = False              # Flag for timing operations
    reading = False            # Flag for shapefile reading status

    shape_df = None            # DataFrame containing shapefile data

    current_db_row = 0         # Tracks current row index for DB insertion
    


    def __init__(self, shape_file_name: str = None, database_name: str = None):
        """
        Initializes the ShapeFileToDB instance with paths to the shapefile and database.

        Args:
            shape_file_name (str): Relative path to the input shapefile (.shp). If just filename then needs to be in working directory.
            database_name (str): Relative path to the output SQLite database.
        """
        if shape_file_name is None:
            shape_file_name = self.SHAPE_FILE_NAME

        if database_name is None:
            database_name = self.DB_NAME

        # Resolve absolute paths for input and output
        self.absolute_file_path = os.path.normpath(os.path.abspath(shape_file_name))
        self.absolute_db_path = os.path.normpath(os.path.abspath(database_name))
        print("Database Path: ", end="", flush=True)
        print_cyan(self.absolute_db_path, flush=True)
        print("Shapefile Path:", end="", flush=True)
        print_cyan(self.absolute_file_path, flush=True)
        self.check_shapefile(shape_file_name=self.absolute_file_path)



    # This is the main method to execute the export process based on paths of shapefiel and database defined in __init__
    def export(self):
        df = self.get_df_from_shapefile()
        if df is not None and not df.empty:
            self.export_shapedf_to_db(zcta_df=df)
            return True
        else:
            print_red("No data to export.")
            return False



    def check_shapefile(self, shape_file_name: str) -> bool:
        """Validates the presence of a shapefile and its required components.

        This method checks whether the provided shapefile path is valid and whether
        the three essential components of a shapefile (.shp, .shx, .dbf) exist in the
        same directory. If any component is missing or the file name is invalid,
        a FileNotFoundError is raised.

        Args:
            shape_file_name (str): Relative or absolute path to the .shp file.

        Returns:
            bool: True if all required shapefile components are found.

        Raises:
            FileNotFoundError: If the file name is invalid or any required component
            (.shp, .shx, .dbf) is missing.
        """
        ERROR_MSG = (
            f"Invalid shapefile name '{shape_file_name}'\n"
            "Shapefile name must end with .shp and not be empty.\n"
            "Shapefile must be in working directory or given relative path.\n"
            "Shapefile must have .shp, .shx, and .dbf files."
        )

        # Normalize and resolve absolute path
        file_path = os.path.normpath(os.path.abspath(shape_file_name))

        # Check if .shp file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(ERROR_MSG)

        # Split file path into root and extension
        root, extension = os.path.splitext(file_path)
        
        # Validate file name and extension
        if not root.strip() or extension.strip().lower() != ".shp":
            raise FileNotFoundError(ERROR_MSG)

        # Construct paths for required companion files
        shx_file = f"{root}.shx"
        dbf_file = f"{root}.dbf"

        # Check existence of .shx and .dbf files
        if not os.path.exists(shx_file) or not os.path.exists(dbf_file):
            raise FileNotFoundError(ERROR_MSG)

        return True

        

    def _read_timer(self):
        """Displays a live timer while reading the shapefile, along with start/end timestamps and row count.

        This method prints:
        - The shapefile name being read.
        - The start time of the read operation.
        - A live-updating timer while `self.timer` is True.
        - The end time and total number of rows read.

        Assumes:
            - `self.absolute_file_path` is set to the shapefile path.
            - `self.LABEL_JUST` and `self.TIMER_JUST` control label and time formatting.
            - `self.shape_df` contains the loaded shapefile data.
            - `print_cyan()` and `print_orange()` are custom print functions for colored output.
        """
        print()

        # Display shapefile name
        print("Shape File:".ljust(self.LABEL_JUST), end="", flush=True)
        file_name = os.path.basename(self.absolute_file_path)
        print_cyan(file_name)

        # Record and display start time
        start_time = datetime.now()
        formatted_start = start_time.strftime("%H:%M:%S:%f")[:self.TIMER_JUST]
        print("Read Start:".ljust(self.LABEL_JUST), end="", flush=True)
        print_cyan(formatted_start)

        # Initialize and display timer
        print("Read Timer:".ljust(self.LABEL_JUST), end="", flush=True)
        timer_str = f"{0:05.2f}"
        print_cyan(timer_str, end="", flush=True)

        # Live timer loop
        while self.timer:
            current_time = datetime.now()
            elapsed_time = current_time - start_time
            total_seconds = elapsed_time.total_seconds()
            timer_str = f"\x1b[5D{total_seconds:05.2f}"  # ANSI escape to overwrite last 5 chars
            print_cyan(timer_str, end="", flush=True)
            time.sleep(0.01)

        # Final timer display
        print_orange(timer_str, flush=True, end="")
        print()

        # Record and display end time
        end_time = start_time + elapsed_time
        formatted_end = end_time.strftime("%H:%M:%S:%f")[:self.TIMER_JUST]
        print("Read End:".ljust(self.LABEL_JUST), end="", flush=True)
        print_orange(formatted_end)

        # Display total rows read
        print("Total Rows:".ljust(self.LABEL_JUST), end="", flush=True)
        print_orange(str(len(self.shape_df)))



    def _read_shape_file(self):
        """Reads the shapefile in chunks and stores the data in a GeoDataFrame.

        This method:
        - Initializes an empty GeoDataFrame (`self.shape_df`).
        - Reads the shapefile incrementally using `self.ROW_INCREMENT` to avoid memory overload.
        - Appends each chunk to `self.shape_df`.
        - Stops reading when no more data is available.
        - Updates `self.reading` and `self.timer` flags accordingly.

        Assumes:
            - `self.absolute_file_path` is a valid path to a shapefile.
            - `self.ROW_INCREMENT` defines the number of rows per read cycle.
            - `self.reading` and `self.timer` are control flags for external timing and status.
        """
        current_row = 0
        self.shape_df = gpd.GeoDataFrame()

        while self.reading:
            # Read a chunk of rows from the shapefile
            gdf_temp = gpd.read_file(
                self.absolute_file_path,
                rows=slice(current_row, current_row + self.ROW_INCREMENT)
            )

            if gdf_temp.empty:
                # No more data to read; stop reading and timer
                self.reading = False
                self.timer = False
            else:
                # Append the chunk to the main DataFrame
                self.shape_df = pd.concat([self.shape_df, gdf_temp], ignore_index=True)
                current_row += self.ROW_INCREMENT

                # Yield control to timer loop without significant delay
                time.sleep(0.01)



    def filter_df(self, df, sort_column):
        """Sorts a DataFrame by the specified column and prints timing information.

        Args:
            df (pd.DataFrame): The DataFrame to be sorted.
            sort_column (str): The column name to sort by.

        Returns:
            pd.DataFrame: A new DataFrame sorted by the specified column.

        Side Effects:
            - Prints the start and end time of the sort operation.
            - Displays the total number of rows in the original DataFrame.
            - Uses custom color functions `print_cyan()` and `print_orange()` for output.

        Assumes:
            - `self.LABEL_JUST` and `self.TIMER_JUST` control label and time formatting.
            - `print_cyan()` and `print_orange()` are available for styled console output.
        """
        print()

        # Record and display start time
        # start_time = datetime.now()
        # formatted_start = start_time.strftime("%H:%M:%S:%f")[:self.TIMER_JUST]
        # print("Sort Start:".ljust(self.LABEL_JUST), end="", flush=True)
        # print_cyan(formatted_start)

        # Perform the sort
        df_sorted = df.sort_values(by=sort_column)

        # Record and display end time
        # end_time = datetime.now()
        # formatted_end = end_time.strftime("%H:%M:%S:%f")[:self.TIMER_JUST]
        # print("Sort End:".ljust(self.LABEL_JUST), end="", flush=True)
        # print_orange(formatted_end)

        # # Display total row count
        # print("Total Rows:".ljust(self.LABEL_JUST), end="", flush=True)
        # print_orange(str(len(df)))
        # print()

        return df_sorted

    
           
    def get_df_from_shapefile(self, shape_file_path: str = None) -> GeoDataFrame:
        """Reads a shapefile into a GeoDataFrame using threaded read and timer operations.

        Args:
            shape_file_path (str, optional): Absolute path to the shapefile.
                If None, uses the path provided during class initialization.

        Returns:
            GeoDataFrame: A sorted GeoDataFrame containing ZIP code data.
            None: If an error occurs or the shapefile is empty.
            False: If the shapefile is found but contains no data.

        Side Effects:
            - Starts two threads: one for reading the shapefile and one for displaying a timer.
            - Sets `self.shape_df` with the loaded data.
            - Prints error messages using `print_red()` if exceptions occur.

        Raises:
            FileNotFoundError: If the shapefile path is invalid.
            DataSourceError: If geopandas fails to read the file.
            Exception: For any other unexpected errors.
        """
        try:
            # Use default path if none provided
            if shape_file_path is None:
                shape_file_path = self.absolute_file_path

            # Initialize threads for reading and timing
            timer_thread = threading.Thread(target=self._read_timer)
            read_thread = threading.Thread(target=self._read_shape_file)

            # Start threads
            self.timer = True
            timer_thread.start()

            self.reading = True
            read_thread.start()

            # Wait for both threads to finish
            read_thread.join()
            timer_thread.join()

            # Retrieve the loaded DataFrame
            zipcode_df = self.shape_df

            if zipcode_df.empty:
                print_red(f"'{shape_file_path}' is empty.")
                return False

            # Sort the DataFrame by ZIP field
            zipcode_df = self.filter_df(zipcode_df, self.ZIP_FIELD)

            return zipcode_df

        except FileNotFoundError as fex:
            print_red(fex)
            raise fex

        except DataSourceError as dbex:
            print_red(dbex)
            raise dbex

        except Exception as ex:
            print_red(ex)
            raise ex

        return None
    


    def export_shapedf_to_db(self, zcta_df) -> bool:
        """Exports ZIP code and ZCTA boundary data from a GeoDataFrame to a SQLite database.

        Args:
            zcta_df (GeoDataFrame): DataFrame containing ZIP code geometries and metadata.

        Returns:
            bool: True if export completes successfully, False if the input is empty.

        Side Effects:
            - Connects to or creates a database using `self.absolute_db_path`.
            - Adds ZIP codes, ZCTA entries, and boundary points to the database.
            - Prints export progress and timing information using styled output.

        Assumes:
            - `AddressDatabase` is a helper class for database operations.
            - `self.ZIP_FIELD`, `self.ZIP_LAT_FIELD`, `self.ZIP_LON_FIELD`, and `self.ZIP_GEOMETRY_FIELD` are valid column names.
            - `print_cyan()` and `print_orange()` are available for styled console output.
        """
        current_row = 0
        start_time = datetime.now()
        current_time = datetime.now()

        # Connect to or create the database
        address_db = AddressDatabase(db_absolute_path=self.absolute_db_path)

        # Display database file name
        print("Database File:".ljust(self.LABEL_JUST), end="", flush=True)
        file_name = os.path.basename(self.absolute_db_path)
        print_cyan(file_name)

        # Display total rows to export
        print("Rows to Export:".ljust(self.LABEL_JUST), end="", flush=True)
        print_cyan(str(len(zcta_df)))

        # Display export start time
        formatted_start = start_time.strftime("%H:%M:%S:%f")[:self.TIMER_JUST]
        print("Export Start:".ljust(self.LABEL_JUST), end="", flush=True)
        print_cyan(formatted_start)

        # Initialize export progress display
        self._print_time_remaining(rows_done=current_row,
                                    total_rows=len(zcta_df),
                                    start_time=start_time,
                                    overwrite=False)

        for _, row in zcta_df.iterrows():
            zip_code = row[self.ZIP_FIELD]
            zip_lat = row[self.ZIP_LAT_FIELD]
            zip_lon = row[self.ZIP_LON_FIELD]
            zip_geometry = row[self.ZIP_GEOMETRY_FIELD]

            # Add ZIP code entry
            zip_obj = address_db.add_zip(zip_code=zip_code, zip_lat=zip_lat, zip_lon=zip_lon)

            if zip_obj is not None:
                try:
                    # Determine if geometry is a MultiPolygon
                    polygons = list(zip_geometry.geoms) if isinstance(zip_geometry, shapely.geometry.MultiPolygon) else [zip_geometry]
                    multi = isinstance(zip_geometry, shapely.geometry.MultiPolygon)

                    for poly in polygons:
                        # Add ZCTA entry for exterior
                        zcta_obj = address_db.add_zcta(zip_code_id=zip_obj.zip_code_id, interior=False, multi=multi)

                        # Add exterior boundary points
                        ext_cord_list = list(poly.exterior.coords)
                        address_db.add_all_zcta_points(zcta_id=zcta_obj.zcta_id, zcta_points=ext_cord_list)

                        # Add interior boundary points (if any)
                        for interior_ring in poly.interiors:
                            zcta_int_obj = address_db.add_zcta(zip_code_id=zip_obj.zip_code_id, interior=True, multi=multi)
                            interior_coord_list = list(interior_ring.coords)
                            address_db.add_all_zcta_points(zcta_id=zcta_int_obj.zcta_id, zcta_points=interior_coord_list)

                except Exception as ex:
                    print_red(ex)

            # Update export progress
            current_row += 1
            time_delta = datetime.now() - current_time
            if time_delta.total_seconds() > 0.5:
                self._print_time_remaining(rows_done=current_row,
                                            total_rows=len(zcta_df),
                                            start_time=start_time,
                                            overwrite=True)
                current_time = datetime.now()
                
        # Final export status
        self._print_time_remaining(rows_done=current_row,
                                    total_rows=len(zcta_df),
                                    start_time=start_time,
                                    overwrite=True)
        current_time = datetime.now()
        
        # Display export end time
        formatted_end = datetime.now().strftime("%H:%M:%S:%f")[:self.TIMER_JUST]
        print("Export End:".ljust(self.LABEL_JUST), end="", flush=True)
        print_orange(formatted_end)
        print()

        return True

    def _print_time_remaining(self, rows_done: int, total_rows: int, start_time: datetime, overwrite: bool = False) -> None:
        """Prints the estimated time remaining for a database export operation.
        """
        if overwrite:
            print("\r", end="")
        print("Rows Exported:".ljust(self.LABEL_JUST), end="", flush=True)
        row_str = f"{str(rows_done).ljust(self.TIMER_JUST)}"
        print_cyan(row_str, end="", flush=True)

        print("Time Remaining:".ljust(self.LABEL_JUST), end="", flush=True)
        time_remaining = self._get_time_remaining(rows_done=rows_done,
                                                    total_rows=total_rows,
                                                    start_time=start_time)
        remaining_str = f"{str(time_remaining).ljust(self.TIMER_JUST)}"
        print_cyan(remaining_str, end="", flush=True)



    def _get_time_remaining(self, rows_done: int, total_rows: int, start_time: datetime) -> str:
        """Estimates the remaining time for a database export operation.

        Args:
            rows_done (int): Number of rows already processed.
            total_rows (int): Total number of rows to process.
            start_time (datetime): Timestamp when the export began.

        Returns:
            str: Estimated time remaining in HH:MM:SS format.

        Notes:
            - Uses linear extrapolation based on elapsed time and rows completed.
            - Returns "00:00:00" if `rows_done` is zero to avoid division by zero.
        """
        if rows_done == 0:
            return "00:00:00"

        rows_left = total_rows - rows_done
        time_lapsed = datetime.now() - start_time
        elapsed_seconds = time_lapsed.total_seconds()

        # Estimate remaining time
        time_left = (rows_left / rows_done) * elapsed_seconds
        hours = int(time_left // 3600)
        minutes = int((time_left % 3600) // 60)
        seconds = int(time_left % 60)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        