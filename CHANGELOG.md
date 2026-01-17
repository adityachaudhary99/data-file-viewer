# Changelog

All notable changes to the "Data File Viewer" extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.1] - 2026-01-17

### Fixed
- Fixed NaN/Infinity serialization errors in pickle and joblib converters
- Fixed pandas DataFrame NaN values causing JSON parsing errors
- Fixed Avro file reading with Snappy compression support
- Fixed GitHub Actions workflow for automated releases
- Improved error handling for missing Python packages

### Changed
- Updated to use Node.js 20 in GitHub Actions workflows
- Improved Python package installation flow

## [1.0.0] - 2026-01-17

### Added
- **Isolated Python Environment:**
  - Extension creates its own private Python virtual environment
  - One-click package installation (no global Python pollution)
  - Automatic setup on first use
  - Cross-session persistence
- **11 File Format Support:**
  - Python Pickle (.pkl, .pickle)
  - HDF5 (.h5, .hdf5)
  - Apache Parquet (.parquet)
  - Apache Feather (.feather)
  - Scikit-learn Joblib (.joblib)
  - NumPy arrays (.npy, .npz)
  - MessagePack (.msgpack)
  - Apache Arrow (.arrow)
  - Apache Avro (.avro)
  - NetCDF (.nc, .nc4)
  - MATLAB (.mat)
- **Features:**
  - Simplify JSON toggle - Switch between detailed and clean views
  - Copy to clipboard functionality
  - Collapse/expand JSON controls
  - Complex number support in all formats
  - Enhanced metadata display
- Initial release with 11 file format support
- Support for `.pkl` / `.pickle` (Python Pickle) files
- Support for `.h5` / `.hdf5` (HDF5) files
- Support for `.parquet` (Apache Parquet) files
- Support for `.feather` (Apache Feather) files
- Support for `.joblib` (Scikit-learn Joblib) files
- Support for `.npy` / `.npz` (NumPy array) files
- Support for `.msgpack` (MessagePack) files
- Support for `.arrow` (Apache Arrow) files
- Support for `.avro` (Apache Avro) files
- Support for `.nc` / `.nc4` (NetCDF) files
- Support for `.mat` (MATLAB) files
- JSON conversion for all file types
- Syntax highlighting for JSON output
- Copy to clipboard functionality
- Collapse/expand JSON view
- File size and metadata display
- Auto-detection of Python installation
- Helpful error messages for missing dependencies
- Truncation of large arrays and dataframes for performance
- Support for nested data structures
- Support for numpy arrays, pandas DataFrames, and custom objects

### Core Features
- Read-only custom editors for all supported file types
- Beautiful syntax-highlighted JSON viewer
- Automatic data type conversion
- Large file handling with smart truncation
- Metadata display for each file type
- **Simplify button** - Toggle between detailed and simplified views
- **Copy to clipboard** - Copy JSON data instantly
- **Collapse/Expand** - Control JSON view depth
- **Auto Python detection** - Finds virtual environments automatically

### Requirements
- Python 3.7 or higher
- Required Python packages: `numpy`, `pandas`, `h5py`, `pyarrow`, `msgpack`, `joblib`, `avro-python3`, `netCDF4`, `scipy`

### Known Issues
- Very large files (>1GB) may take time to load
- Some custom pickle objects may not serialize perfectly to JSON
- Pickle files from untrusted sources should not be opened (security risk)

### Security
- Added warning for pickle file deserialization
- Read-only access to all files
- No file modification capabilities

---

## Future Plans

### [1.1.0] - Planned
- [ ] Add search functionality within JSON view
- [ ] Add filter/query capabilities for large datasets
- [ ] Add export to CSV/Excel functionality
- [ ] Add statistical summary for numerical data
- [ ] Add configuration options (max preview size, Python path, etc.)

### [1.2.0] - Planned
- [ ] Add data visualization (charts/plots)
- [ ] Add table view for tabular data
- [ ] Add diff view for comparing files
- [ ] Performance improvements for very large files (streaming)

### [2.0.0] - Future
- [ ] Add support for more formats (Zarr, TFRecord, etc.)
- [ ] Interactive data exploration
- [ ] Edit support for some formats
- [ ] Cloud file support (S3, GCS, Azure)

---

[Unreleased]: https://github.com/adityachaudhary99/data-file-viewer/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/adityachaudhary99/data-file-viewer/releases/tag/v1.0.0
