# IDA Library Python Module

The IDA Library Python module enables running IDA Pro as an independent Python package outside the IDA UI environment, allowing for programmatic binary analysis and reverse engineering tasks.

## Prerequisites

### Environment Setup

Set the `IDADIR` environment variable to point to your IDA installation directory:

**Linux/macOS:**
```bash
export IDADIR="/path/to/your/ida/installation"
```

**Windows:**
```cmd
set IDADIR="C:\Program Files\IDA Pro 9.1"
```

**Example paths:**
- **macOS:** `/Applications/IDA Professional 9.1.app/Contents/MacOS/`
- **Windows:** `C:\Program Files\IDA Pro 9.1\`
- **Linux:** `/opt/ida-9.1/`

> **Note:** If you have already installed and configured the `idapro` Python package in the past using script provided with IDA installation package, setting `IDADIR` is not required.

## Usage Example

```python
# You need to import first idapro module
import idapro
# After idapro module is loaded, you can import IDA Python modules
import idautils
import ida_funcs
import ida_name

# Open the database using idapro module
if idapro.open_database("program.exe", True) == 0:
    # Iterate functions and print basic information for each of them
    for func_ea in idautils.Functions():
        f = ida_funcs.get_func(func_ea)
        func_name = ida_name.get_name(func_ea)
        print(f"Function - name {func_name}, start ea {hex(f.start_ea)}, end ea {hex(f.end_ea)}")

    # Close database discarding the changes
    idapro.close_database(False)
```

**For a complete traversing database example, see:** [traverse.py](./examples/traverse.py)

## Troubleshooting

### Common Issues

**ModuleNotFoundError: No module named 'idapro'**
- Ensure `IDADIR` is set correctly
- Verify IDA Pro is properly installed

**License Issues**
- Ensure you have a valid IDA Pro license
- Check that IDA can run normally in GUI mode first

## API Reference

For detailed API documentation, refer to:
- IDA Python documentation at [https://python.docs.hex-rays.com/](https://python.docs.hex-rays.com/)
- Built-in help: `help(idapro)` after importing
- IDA Pro SDK documentation at [https://docs.hex-rays.com/developer-guide/c++-sdk](https://docs.hex-rays.com/developer-guide/c++-sdk)