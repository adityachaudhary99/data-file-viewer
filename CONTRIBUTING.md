# Contributing to Data File Viewer

Thank you for your interest in contributing! 🎉

## How to Contribute

### Reporting Bugs

1. Check if the bug is already reported in [Issues](https://github.com/adityachaudhary99/data-file-viewer/issues)
2. If not, create a new issue with:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, VS Code/Cursor version, Python version)
   - Sample file (if possible)

### Suggesting Features

1. Check existing [Issues](https://github.com/adityachaudhary99/data-file-viewer/issues) for similar suggestions
2. Create a new issue describing:
   - The feature you'd like
   - Why it would be useful
   - How it might work

### Adding New File Format Support

To add support for a new file format:

1. Create a Python converter in `python/convert_newformat.py`
2. Create a TypeScript provider in `src/providers/NewFormatEditorProvider.ts`
3. Register it in `src/extension.ts`
4. Add to `package.json` under `customEditors` and `activationEvents`
5. Update `README.md` and `CHANGELOG.md`
6. Add Python dependencies to `python/requirements.txt`

### Development Setup

```bash
# Clone the repository
git clone https://github.com/adityachaudhary99/data-file-viewer.git
cd data-file-viewer

# Install dependencies
npm install
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
pip install -r python/requirements.txt

# Compile
npm run compile

# Test
Press F5 in VS Code to launch Extension Development Host
```

### Code Style

- Use TypeScript for extension code
- Use Python 3.7+ for converters
- Follow existing code patterns
- Add comments for complex logic
- Keep functions focused and small

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages (`git commit -m 'Add support for XYZ format'`)
6. Push to your fork (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Testing

Before submitting a PR:
- Test with various file sizes (small, medium, large)
- Test error cases (corrupted files, missing dependencies)
- Verify all existing formats still work
- Update documentation if needed

## Questions?

Feel free to open an issue for any questions!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
