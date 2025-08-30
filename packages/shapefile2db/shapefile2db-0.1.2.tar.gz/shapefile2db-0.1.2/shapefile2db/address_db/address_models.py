"""SQLAlchemy ORM models for ZIP code and ZCTA data.

Defines the database schema for ZIP codes, ZCTAs (Zip Code Tabulation Areas),
and the geospatial points that compose each ZCTA.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ZipCode(Base):
    """Represents a ZIP code with associated latitude and longitude.

    Attributes:
        zip_code_id (int): Primary key, unique identifier.
        zip_code (str): ZIP code string (e.g., '92101').
        zip_lat (float): Latitude of the ZIP code centroid.
        zip_lon (float): Longitude of the ZIP code centroid.
    """

    __tablename__ = 'zip_codes'

    zip_code_id = Column(Integer, primary_key=True, unique=True)
    zip_code = Column(String, nullable=False)
    zip_lat = Column(Float, nullable=False)
    zip_lon = Column(Float, nullable=False)

    def __repr__(self):
        return (
            f"<ZipCode(zip_code_id={self.zip_code_id}, "
            f"zip_code='{self.zip_code}', "
            f"zip_lat={self.zip_lat}, "
            f"zip_lon={self.zip_lon})>"
        )


class ZCTA(Base):
    """Represents a Zip Code Tabulation Area (ZCTA) linked to a ZIP code.

    Attributes:
        zcta_id (int): Primary key.
        zip_code_id (int): Foreign key linking to ZipCode.
        interior (bool): True if this shape is interior (excluded from exterior ZCTA).
        multi (bool): True if the ZCTA consists of multiple disjoint shapes.
    """

    __tablename__ = 'zctas'

    zcta_id = Column(Integer, primary_key=True)
    zip_code_id = Column(Integer)
    interior = Column(Boolean)
    multi = Column(Boolean)

    def __repr__(self):
        return (
            f"<ZCTA(zcta_id={self.zcta_id}, "
            f"zip_code_id={self.zip_code_id}, "
            f"interior={self.interior}, "
            f"multi={self.multi})>"
        )


class ZCTAPoint(Base):
    """Represents a geospatial point that defines the shape of a ZCTA.

    Attributes:
        zcta_point_id (int): Primary key.
        zcta_id (int): Foreign key linking to ZCTA.
        zcta_point_lat (float): Latitude of the point.
        zcta_point_lon (float): Longitude of the point.
    """

    __tablename__ = 'zcta_points'

    zcta_point_id = Column(Integer, primary_key=True)
    zcta_id = Column(Integer)
    zcta_point_lat = Column(Float)
    zcta_point_lon = Column(Float)

    def __repr__(self):
        return (
            f"<ZCTAPoint(zcta_point_id={self.zcta_point_id}, "
            f"zcta_id={self.zcta_id}, "
            f"zcta_point_lat={self.zcta_point_lat}, "
            f"zcta_point_lon={self.zcta_point_lon})>"
        )