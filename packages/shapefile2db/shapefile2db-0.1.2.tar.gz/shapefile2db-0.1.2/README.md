<p align="center">
  <img src="https://github.com/rlapine/shapefile2db/blob/624aa335a27f6db7b56f53907ff8aecf3f031ba7/shapefile2db/assets/ShapeFile2DB_logo.png?raw=true" alt="shapefile2db logo" width="400"/>
</p>

---

### ShapeFile2DB V 0.1.2

Exports US Census ZCTA (Zip Code Tabulation Area) shapefiles to a SQLite database via CLI or Python API.

---

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/rlapine/shapefile2db?style=social)](https://github.com/rlapine/shapefile2db/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/rlapine/shapefile2db?style=social)](https://github.com/rlapine/shapefile2db/network/members)

---

## Overview

ZipShapeFile2DB is a Python package for extracting, filtering, and exporting ZIP Code Tabulation Area (ZCTA) shapefiles into structured formats for geospatial analysis in a SQLite3 database file. 

Designed for developers and data analysts, it offers a clean command-line interface and a modular API that integrates seamlessly into Python workflows.

Whether you're automating shapefile exports, building spatial dashboards, or prepping data for SQL-based queries, ZipShapeFile2DB provides a transparent, scriptable pipeline with real-time logging, schema validation, and flexible output options.

---

## Shapefile Requirements

This module is designed to work with shapefiles derived from the 2020 ZCTA dataset
provided by the US Census Bureau.

To download the official shapefiles, visit:
https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-files.2020.html

This download will provid a zipped file containing all of the shapefile components (several files)

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

---

## Features

- **CLI & API support** for ZCTA shapefile export  
- **Modular architecture** for easy extension and testing  
- **Google-style docstrings** for clarity and discoverability  
- **Built-in validation** for input paths and schema integrity  
- **Geospatial stack ready**: works with `geopandas`, `shapely`, and `SQLAlchemy`

---

### Installation

```bash
pip install shapefile2db
```

Or for local development:

```bash
git clone https://github.com/rlapine/shapefile2db.git
cd shapefile2db
pip install -e .
```

---

## Dependencies

- Python 3.8+
- geopandas==1.1.1",
- pandas==2.3.2",
- printpop==0.2.2",
- pyogrio==0.11.0",
- setuptools==80.9.0",
- Shapely==2.1.1",
- SQLAlchemy==2.0.43"

---

### API Example

```python
from shapefile2db import export_shapefile_to_db

export_shapefile_to_db(state="NY",
                      shape_file_name="tl_2020_us_zcta520.shp", 
                      database_name="ny_address.db")

```

---

### Example Output

```text
Shape File: tl_2020_us_zcta520.shp
Read Start: 12:51:49:25
Read Timer: 03.20
Read End: 12:51:52:45
Total Rows: 33791

Filter 'NY' Start: 12:51:52:47
Filter End: 12:51:52:48
Total 'NY' Rows: 1826

Warning: Database file not found at: 'C:\Users\ryan\Visual Code Projects\shapefile\ny_address.db'
Warning: Database file created at: 'C:\Users\ryan\Visual Code Projects\shapefile\ny_address.db'

Database File: ny_address.db
Rows to Export: 1826
Export Start: 12:51:52:48
Rows Exported: 596 Time Remaining: 00:00:46.
```

---

### 🖥️ CLI Demo

![CLI Export Demo](https://github.com/rlapine/shapefile2db/blob/624aa335a27f6db7b56f53907ff8aecf3f031ba7/shapefile2db/assets/ShapeFile2DB_output.gif?raw=true)

---

### Project Structure

```
shapefile2db/
├── shapefile2db/
│   ├── cli.py                      # CLI entry point
│   ├── core.py                     # Main export logic
│   ├── shape_file_exporter.py      # Exporter class
│   ├── state_shape_file_exporter.py# Individual state exporter
│   └── address_db/                 # Subpackage for database logic
│       ├── __init__.py             # Address DB API exposure
│       ├── address_constants.py    # state constants
│       ├── address_database.py     # DB connection and export logic
│       └── address_models.py       # ORM models
├── cli.py                          # CLI entry point
├── core.py                         # Main export wrapper
├── __init__.py                     # API exposure
├── LICENSE                         # Project license
├── pyproject.toml                  # Build system and CLI entry points
├── requirements.txt                # Runtime dependencies
└── README.md                       # Project overview and usage
```

---

## Contributing

Pull requests welcome! If you spot formatting quirks, want to add new named colors or extend features (like terminal detection or theme presets), feel free to collaborate.

To contribute:

Fork the repo

Add your changes with Google-style comments

Submit a pull request with a clear description

For style consistency, follow the Python Google Style Guide for functions and comments.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Author

Created by Ryan LaPine [@rlapine](https://github.com/rlapine) — a technically skilled developer focused on clarity, maintainability, and audience-ready documentation. This class is part of a broader effort to build reusable, well-documented tools for data-driven projects.

---

## Contact

Feel free to reach out with questions or collaboration ideas:

📧 github.stunt845@passinbox.com  
🔗 GitHub: [@rlapine](https://github.com/rlapine)