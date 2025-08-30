"""Provides access to the address.db SQLite database.

Initializes the database engine, creates tables if the database file is missing,
and handles connection setup using SQLAlchemy.

Creates the db and tables for storing ZIP code and ZCTA data.

Classes:
    AddressDatabase: Manages connection and initialization of the address.db file.
"""

import os

# SQLAlchemy imports
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

# Local imports
from shapefile2db.address_db.address_models import ZipCode, ZCTA, ZCTAPoint, Base

# IO and console output
from printpop import print_cyan, print_red, print_orange


class AddressDatabase:
    """Handles access to the address.db SQLite database.

    Attributes:
        DEFAULT_DB_PATH (str): Default relative path to the database file.
        LABEL_JUST (int): Padding for console output labels.
        engine (Engine): SQLAlchemy engine instance.
        db_absolute_path (str): Absolute path to the database file.
    """

    DEFAULT_DB_PATH = 'address.db'
    LABEL_JUST = 20

    engine = None
    db_absolute_path = None

    
    
    def __init__(self, db_relative_path=DEFAULT_DB_PATH, db_absolute_path=None):
        """Initializes the AddressDatabase instance.

        If the database file does not exist, it will be created along with required tables.

        Args:
            db_relative_path (str): Relative path to the database file.
            db_absolute_path (str, optional): Absolute path to the database file.

        Raises:
            ValueError: If path resolution fails.
            FileNotFoundError: If the database file cannot be located.
            SQLAlchemyError: If SQLAlchemy fails to initialize the engine or create tables.
            Exception: For any other unexpected errors.
        """
        try:
            # Resolve absolute path
            if db_absolute_path is not None:
                self.db_absolute_path = db_absolute_path
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                self.db_absolute_path = os.path.normpath(
                    os.path.join(base_dir, db_relative_path)
                )

            # Check if database file exists
            create_tables = False
            if not os.path.exists(self.db_absolute_path):
                print("Warning:".ljust(self.LABEL_JUST), end="", flush=True)
                print_orange("Database file not found at: ", end="", flush=True)
                print_cyan(f"'{self.db_absolute_path}'", flush=True)
                create_tables = True

            # Initialize SQLAlchemy engine
            self.engine = create_engine(f"sqlite:///{self.db_absolute_path}")

            # Create tables if needed
            if create_tables:
                Base.metadata.create_all(self.engine)
                print("Warning:".ljust(self.LABEL_JUST), end="", flush=True)
                print_orange("Database file created at: ", end="", flush=True)
                print_cyan(f"'{self.db_absolute_path}'", flush=True)

        except ValueError as ve:
            print_red(f"ValueError occurred in AddressDatabase: {ve}")
        except FileNotFoundError as fnfe:
            print_red(f"FileNotFoundError occurred in AddressDatabase: {fnfe}")
        except SQLAlchemyError as sae:
            print_red(f"SQLAlchemyError occurred in AddressDatabase: {sae}")
        except Exception as e:
            print_red(f"Unexpected error in AddressDatabase: {type(e).__name__}: {e}")
    


    def add_zip(self, zip_code: str, zip_lat: float, zip_lon: float):
        """Adds a new ZipCode record to the database.

        Args:
            zip_code: ZIP code as a string.
            zip_lat: Latitude of the ZIP code.
            zip_lon: Longitude of the ZIP code.

        Returns:
            ZipCode: The newly created ZipCode object, or None if failed.
        """
        session = None
        try:
            Session = sessionmaker(bind=self.engine)
            with Session() as session:
                new_zip = ZipCode(zip_code=zip_code, zip_lat=zip_lat, zip_lon=zip_lon)
                session.add(new_zip)
                session.commit()
                session.refresh(new_zip)
                return new_zip
        except (TypeError, ValueError) as model_error:
            print_red(f"ValueError in add_zip(): {model_error}")
        except SQLAlchemyError as db_error:
            print_red(f"SQLAlchemyError in add_zip(): {db_error}")
        except Exception as e:
            print_red(f"Unexpected error in add_zip(): {type(e).__name__}: {e}")
        if session:
            session.rollback()
        return None

    
    
    def get_zips(self, zip_code: str = None):
        """Retrieves ZipCode records matching the given ZIP code.

        Args:
            zip_code: Optional ZIP code to filter by.

        Returns:
            List[ZipCode]: Matching ZipCode records, or all if no filter is provided.
        """
        try:
            Session = sessionmaker(bind=self.engine)
            with Session() as session:
                query = session.query(ZipCode)
                if zip_code:
                    query = query.filter(ZipCode.zip_code == zip_code)
                return query.all()
        except SQLAlchemyError as db_error:
            print_red(f"SQLAlchemyError in get_zips(): {db_error}")
        except Exception as e:
            print_red(f"Unexpected error in get_zips(): {type(e).__name__}: {e}")
        return []

   
   
    def add_zcta(self, zip_code_id: int, interior: bool, multi: bool):
        """Adds a new ZCTA record linked to a ZipCode.

        Args:
            zip_code_id: Foreign key ID of the ZipCode.
            interior: Whether the ZCTA is interior.
            multi: Whether the ZCTA is multi-part.

        Returns:
            ZCTA: The newly created ZCTA object, or None if failed.
        """
        session = None
        try:
            Session = sessionmaker(bind=self.engine)
            with Session() as session:
                new_zcta = ZCTA(zip_code_id=zip_code_id, interior=interior, multi=multi)
                session.add(new_zcta)
                session.commit()
                session.refresh(new_zcta)
                return new_zcta
        except (TypeError, ValueError) as model_error:
            print_red(f"ValueError in add_zcta(): {model_error}")
        except SQLAlchemyError as db_error:
            print_red(f"SQLAlchemyError in add_zcta(): {db_error}")
        except Exception as e:
            print_red(f"Unexpected error in add_zcta(): {type(e).__name__}: {e}")
        if session:
            session.rollback()
        return None

    
    
    def get_zctas(self, zip_code_id: int):
        """Retrieves all ZCTA records linked to a given ZipCode.

        Args:
            zip_code_id: Foreign key ID of the ZipCode.

        Returns:
            List[ZCTA]: Matching ZCTA records, or empty list if none found.
        """
        try:
            Session = sessionmaker(bind=self.engine)
            with Session() as session:
                return session.query(ZCTA).filter(ZCTA.zip_code_id == zip_code_id).all()
        except SQLAlchemyError as db_error:
            print_red(f"SQLAlchemyError in get_zctas(): {db_error}")
        except Exception as e:
            print_red(f"Unexpected error in get_zctas(): {type(e).__name__}: {e}")
        return []

    
    
    def add_all_zcta_points(self, zcta_id: int, zcta_points: list[tuple[float, float]]):
        """Adds multiple ZCTAPoint records for a given ZCTA.

        Args:
            zcta_id: Foreign key ID of the ZCTA.
            zcta_points: List of (longitude, latitude) tuples.
            NOTE: IN SHAPEFILE LONGITUDE COMES FIRST THEN LATITUDE

        Returns:
            bool: True if successful, False otherwise.
        """
        session = None
        try:
            Session = sessionmaker(bind=self.engine)
            with Session() as session:
                # NOTE: longitude comes first in SHAPEFILE
                for lon, lat  in zcta_points:
                    new_point = ZCTAPoint(zcta_id=zcta_id, zcta_point_lat=lat, zcta_point_lon=lon)
                    session.add(new_point)
                session.commit()
                return True
        except (TypeError, ValueError) as model_error:
            print_red(f"ValueError in add_all_zcta_points(): {model_error}")
        except SQLAlchemyError as db_error:
            print_red(f"SQLAlchemyError in add_all_zcta_points(): {db_error}")
        except Exception as e:
            print_red(f"Unexpected error in add_all_zcta_points(): {type(e).__name__}: {e}")
        if session:
            session.rollback()
        return False

    
    
    def add_zcta_point(self, zcta_id: int, zcta_point_lat: float, zcta_point_lon: float):
        """Adds a single ZCTAPoint record for a given ZCTA.

        Args:
            zcta_id: Foreign key ID of the ZCTA.
            zcta_point_lat: Latitude of the point.
            zcta_point_lon: Longitude of the point.

        Returns:
            ZCTAPoint: The newly created ZCTAPoint object, or None if failed.
        """
        session = None
        try:
            Session = sessionmaker(bind=self.engine)
            with Session() as session:
                new_point = ZCTAPoint(
                    zcta_id=zcta_id,
                    zcta_point_lat=zcta_point_lat,
                    zcta_point_lon=zcta_point_lon
                )
                session.add(new_point)
                session.commit()
                session.refresh(new_point)
                return new_point
        except (TypeError, ValueError) as model_error:
            print_red(f"ValueError in add_zcta_point(): {model_error}")
        except SQLAlchemyError as db_error:
            print_red(f"SQLAlchemyError in add_zcta_point(): {db_error}")
        except Exception as e:
            print_red(f"Unexpected error in add_zcta_point(): {type(e).__name__}: {e}")
        if session:
            session.rollback()
        return None

    
    
    def get_zcta_points(self, zcta_id: int):
        """Retrieves all ZCTAPoint records for a given ZCTA.

        Args:
            zcta_id: Foreign key ID of the ZCTA.

        Returns:
            List[ZCTAPoint]: Matching ZCTAPoint records, or empty list if none found.
        """
        try:
            Session = sessionmaker(bind=self.engine)
            with Session() as session:
                return session.query(ZCTAPoint).filter(ZCTAPoint.zcta_id == zcta_id).all()
        except SQLAlchemyError as db_error:
            print_red(f"SQLAlchemyError in get_zcta_points(): {db_error}")
        except Exception as e:
            print_red(f"Unexpected error in get_zcta_points(): {type(e).__name__}: {e}")
        return []