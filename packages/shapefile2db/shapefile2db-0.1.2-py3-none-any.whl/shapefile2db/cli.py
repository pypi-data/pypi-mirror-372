#!/usr/bin/env python

from shapefile2db.shape_file_exporter import ShapeFileToDB
from shapefile2db.core import export_shapefile_to_db
from printpop import print_bold, print_red, print_green

def main():
    """Runs the console interface loop for demonstrating shapefile export functionality.

    Provides a menu-driven CLI for validating shapefiles and exporting ZCTA data
    to a SQLite database. Options include checking shapefile validity, exporting
    by state, and exporting all states.
    """
    print()
    print_bold("ShapeFileExporter - Export ZCTA Shapefiles to a SQLite Database File")

    user_continue = True
    while user_continue:
        # Display menu options
        print()
        print_bold("Options")
        print("1) Check for valid shapefile and path.")
        print("2) Export By State.")
        print("3) Export All States.")
        print("q) Exit.")
        print()
        print_bold("Enter an option:", end='')
        option = input().strip().lower()
        print()

        match option:
            case '1':
                # Option 1: Validate shapefile path
                print_bold("Enter path and filename of the shapefile (.shp):", end='')
                shapefile_name = input().strip()
                try:
                    ShapeFileToDB().check_shapefile(shape_file_name=shapefile_name)
                    print("The shapefile ", end="")
                    print_green(f"'{shapefile_name}'", end="")
                    print(" was found and is valid.")
                except Exception as e:
                    print_red("Error:", e)

            case '2':
                # Option 2: Export data for a single state
                print_bold("Enter a two-letter abbreviation for the state:", end='')
                state = input().strip().upper()
                print_bold("Enter path and filename of the shapefile (.shp):", end='')
                shapefile_name = input().strip()
                print_bold("Enter the name of the database file to export to (.db):", end='')
                database_name = input().strip()
                try:
                    export_shapefile_to_db(
                        state=state,
                        shape_file_name=shapefile_name,
                        database_name=database_name
                    )
                except Exception as e:
                    print_red("Error:", e)

            case '3':
                # Option 3: Export data for all states
                print_bold("Enter path and filename of the shapefile (.shp):", end='')
                shapefile_name = input().strip()
                print_bold("Enter the name of the database file to export to (.db):", end='')
                database_name = input().strip()
                try:
                    export_shapefile_to_db(
                        shape_file_name=shapefile_name,
                        database_name=database_name
                    )
                except Exception as e:
                    print_red("Error:", e)

            case _:
                # Option q or any other input: Exit loop
                user_continue = False
                print_bold("Bye!")
                print()


if __name__ == "__main__":
    main()