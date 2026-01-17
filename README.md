# Data File Viewer

View and explore binary data files directly in VS Code and Cursor IDE.

## Supported File Types

- **`.pkl` / `.pickle`** - Python Pickle files
- **`.h5` / `.hdf5`** - HDF5 files
- **`.parquet`** - Apache Parquet files
- **`.feather`** - Apache Feather files
- **`.joblib`** - Scikit-learn Joblib files
- **`.npy` / `.npz`** - NumPy array files
- **`.msgpack`** - MessagePack files
- **`.arrow`** - Apache Arrow files
- **`.avro`** - Apache Avro files
- **`.nc` / `.nc4`** - NetCDF files
- **`.mat`** - MATLAB files

## Features

- 🔍 **Explore structure** - Navigate nested data hierarchies
- 📊 **Preview data** - View arrays, dataframes, and objects
- 🔒 **Safe viewing** - Read-only access to your data files
- 🎨 **Syntax highlighting** - Clear visualization of data types
- ⚡ **Fast loading** - Efficient handling of large files
- 🎯 **Simplify view** - Toggle between detailed and simplified JSON views
- 📋 **Copy to clipboard** - Easily copy JSON data
- 🔄 **Collapse/Expand** - Control JSON view depth

## Usage

Simply click on any supported file in your workspace. The extension will automatically open it in a custom viewer.

## Security Note

⚠️ **Pickle files warning**: Opening `.pkl` and `.joblib` files executes Python code during deserialization. Only open pickle files from trusted sources.

## Requirements

This extension uses Python to read data files. Make sure you have:
- Python 3.7 or higher installed
- Required Python packages: `numpy`, `pandas`, `h5py`, `pyarrow`, `msgpack`, `joblib`, `avro-python3`, `netCDF4`, `scipy`

Install all at once:
```bash
pip install numpy pandas h5py pyarrow msgpack joblib avro-python3 netCDF4 scipy
```

The extension will automatically detect your Python installation.

## Extension Settings

Currently, this extension works out of the box with no configuration needed.

## Known Issues

- Very large files (>1GB) may take time to load
- Some custom pickle objects may not serialize to JSON properly

## Release Notes

### 1.0.0

Comprehensive first release with support for 11 file formats:
- Pickle files (.pkl, .pickle)
- HDF5 files (.h5, .hdf5)
- Apache Parquet files (.parquet)
- Apache Feather files (.feather)
- Joblib files (.joblib)
- NumPy files (.npy, .npz)
- MessagePack files (.msgpack)
- Apache Arrow files (.arrow)
- Apache Avro files (.avro)
- NetCDF files (.nc, .nc4)
- MATLAB files (.mat)

Features:
- JSON conversion with syntax highlighting
- Simplify toggle for cleaner views
- Copy to clipboard
- Collapse/Expand controls
- Smart truncation for large files
- Metadata display
- Auto-detection of Python virtual environments

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Found a bug or have a feature request? Please open an issue on [GitHub](https://github.com/adityachaudhary99/data-file-viewer).

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the Cursor IDE community
- Inspired by the need for better data file viewing in Open VSX
- Thanks to all the open-source Python libraries that make this possible

## ⭐ Support

If you find this extension useful, please:
- ⭐ Star the repository on GitHub
- 📝 Leave a review on Open VSX
- 🐛 Report bugs or suggest features
- 🤝 Contribute code or documentation

---

Made with ❤️ for data scientists and ML engineers
