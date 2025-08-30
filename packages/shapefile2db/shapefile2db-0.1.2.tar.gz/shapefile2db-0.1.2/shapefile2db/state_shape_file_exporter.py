"""
StateShapeFileToDB

Extends ShapeFileToDB to export ZIP code geometry data for a single U.S. state
from the 2020 ZCTA shapefile provided by the US Census Bureau.

Use this class when exporting data for one state only. For all-state exports,
use ShapeFileToDB.
"""

from shapefile2db.shape_file_exporter import ShapeFileToDB
from shapefile2db.address_db.address_constants import STATE_ZIP_RANGES
from datetime import datetime
from printpop import print_lime, print_cyan, print_orange, print_red
from functools import reduce


class StateShapeFileToDB(ShapeFileToDB):
    """Exports ZIP code geometries for a single state to a SQLite database.

    This class filters ZIP code geometries based on state-specific ZIP ranges
    and stores the results in a state-named SQLite database.

    Attributes:
        DB_BASE (str): Suffix used for default database naming.
        state (str): Two-letter state abbreviation.
        zip_ranges_list (List[Tuple[int, int]]): List of ZIP code ranges for the state.
    """

    DB_BASE = "_address.db"
    state = None
    zip_ranges_list = None



    def __init__(self, state: str, shape_file_name: str = None, database_name: str = None):
        """Initializes the state-specific exporter.

        Args:
            state (str): Two-letter abbreviation of the state (e.g., 'CA', 'TX').
            shape_file_name (str, optional): Path to the .shp file. If None, uses default.
            database_name (str, optional): Name of the SQLite database. If None, uses default.

        Raises:
            ValueError: If the provided state is not a valid abbreviation in STATE_ZIP_RANGES.
        """
        if not isinstance(state, str) or state.upper() not in STATE_ZIP_RANGES:
            raise ValueError(
                f"State '{state}' is not a valid state abbreviation. "
                "Please use a valid two-letter abbreviation (e.g., 'CA', 'TX')."
            )

        self.state = state.upper()
        self.zip_ranges_list = STATE_ZIP_RANGES.get(self.state)

        if database_name is None:
            # Default database name: e.g., 'ca_address.db'
            database_name = f"{self.state.lower()}{self.DB_BASE}"

        # Initialize parent class with shape file and database name
        super().__init__(shape_file_name=shape_file_name, database_name=database_name)



    def filter_df(self, df, sort_column=None):
        """Filters and sorts a DataFrame by ZIP code ranges for the specified state.

        Args:
            df (pd.DataFrame): The input DataFrame containing ZIP code data.
            sort_column (str, optional): Column to sort by. Defaults to ZIP_FIELD.

        Returns:
            pd.DataFrame: Filtered and sorted DataFrame containing only rows for the state.

        Side Effects:
            - Prints start and end timestamps of the filtering operation.
            - Displays total row count after filtering.
            - Uses styled console output via print_cyan() and print_orange().

        Assumes:
            - `self.ZIP_FIELD` is defined in the parent class.
            - `self.LABEL_JUST` and `self.TIMER_JUST` control output formatting.
        """
        # Build list of filters for each ZIP code range
        filter_list = []
        for zip_range in self.zip_ranges_list:
            low_zip_filter = df[self.ZIP_FIELD] >= zip_range[0]
            high_zip_filter = df[self.ZIP_FIELD] <= zip_range[1]
            filter_list.append(low_zip_filter & high_zip_filter)

        # Combine all filters using bitwise OR
        combined_filter = reduce(lambda x, y: x | y, filter_list)

        # Record and print start time
        start_time = datetime.now()
        formatted_start = start_time.strftime("%H:%M:%S:%f")[:self.TIMER_JUST]
        print(f"Filter '{self.state}' Start:".ljust(self.LABEL_JUST), end="", flush=True)
        print_cyan(formatted_start)

        # Apply filter and sort
        filtered_df = df[combined_filter]
        sort_column = sort_column or self.ZIP_FIELD
        df_sorted = filtered_df.sort_values(by=sort_column)

        # Record and print end time
        end_time = datetime.now()
        formatted_end = end_time.strftime("%H:%M:%S:%f")[:self.TIMER_JUST]
        print("Filter End:".ljust(self.LABEL_JUST), end="", flush=True)
        print_orange(formatted_end)

        # Print total row count
        print(f"Total '{self.state}' Rows:".ljust(self.LABEL_JUST), end="", flush=True)
        print_orange(str(len(df_sorted)))

        return df_sorted