# Data File Viewer

View and explore binary data files directly in VS Code (and compatible editors like Cursor).

## What's New in 2.0

The Data File Viewer is now an interactive explorer & profiler. Beyond the original JSON view, you now get sortable tables for tabular data, 2-D grids for arrays with profiling statistics (shape, dtype, min/max/mean/std, distribution histograms), hierarchical tree navigation for complex files (HDF5, NetCDF, MATLAB), and CSV export for your results. The original Raw JSON view is preserved as a tab for every file type.

## Supported File Types

- **`.pkl` / `.pickle`** - Python Pickle files
- **`.h5` / `.hdf5`** - HDF5 files
- **`.parquet`** - Apache Parquet files
- **`.feather`** - Apache Feather files
- **`.joblib` / `.jl`** - Scikit-learn Joblib files
- **`.npy` / `.npz`** - NumPy array files
- **`.msgpack` / `.mp`** - MessagePack files
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

**Python 3.7 or higher** must be installed on your system.

### First-Time Setup

When you first open a data file, the extension will:
1. **Automatically create** its own isolated Python environment
2. **Ask permission** to install required packages (one-time setup)
3. **Install packages** in its own environment (doesn't affect your global Python!)

**That's it!** The setup takes ~2-3 minutes the first time, then works forever.

### Why This Approach?

- ✅ **Isolated**: Doesn't pollute your global Python packages
- ✅ **Persistent**: Packages installed once, work everywhere
- ✅ **Clean**: Uninstall the extension = removes everything
- ✅ **No conflicts**: Won't interfere with your projects

## Extension Settings

Currently, this extension works out of the box with no configuration needed.

## Known Issues

- Very large files (>1GB) may take time to load
- Some custom pickle objects may not serialize to JSON properly

## Release notes are in [CHANGELOG.md](CHANGELOG.md)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Found a bug or have a feature request? Please open an issue on [GitHub](https://github.com/adityachaudhary99/data-file-viewer).

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

If you find this extension useful, please:
- Star the repository on GitHub
- Leave a review on the VS Code Marketplace and Open VSX
- Report bugs or suggest features
- Contribute code or documentation
