# pygridgain
GridGain 9 Python Client.

## Prerequisites

- Python 3.9 or above (3.9, 3.10, 3.11, 3.12 and 3.13 are tested);
- Access to GridGain 9 node, local or remote.

## Installation

### From repository
This is the recommended way for users. If you only want to use the `pygridgain` module in your project, do:
```
$ pip install pygridgain>=9
```

### From sources
This way is more suitable for developers, or if you install the client from zip archive.
1. Download and/or unzip GridGain 9 Python Client sources to `pygridgain_path`;
2. Go to `pygridgain_path` folder;
3. Execute `pip install -e .`.

```bash
$ cd <pygridgain_path>
$ pip install -e .
```

This will install the repository version of `pygridgain` into your environment in so-called “develop” or “editable”
mode. You may read more about [editable installs](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs)
in the `pip` manual.

### *C++ extension*

The core of the package is a C++ extension. It shares the code with the GridGain C++ Client. The package is pre-built
for the most common platforms, but you may need to build it if your platform is not included.

We use `cibuildwheel` to build wheels, mainly using GitHub Actions workflow, but in case you need it, you can do it on
you platform manually.

General requirements:
- C++17 compatible compiler (GCC and G++ for Linux, MSVC 14.x+ for Windows, CLang for MacOS);
- CMake version >=3.18;

For building `wheels` do the following steps:
1. Install `cibuildwheel` utility (we use version 2.23.1):
   ```bash
   python -m pip install cibuildwheel==2.23.1
   ```
2. Set `CIBW_BUILD` environment variable to a desired value. We use the following values:
   - macOS and Windows: `CIBW_BUILD = cp39-* cp310-* cp311-* cp312-* cp313-*`;
   - Linux: `CIBW_BUILD: cp39-manylinux* cp31{0,1,2,3}-manylinux*`.
3. Set `CIBW_ARCHS` environment variable to a desired value. We use the following values:
   - MacOS 14: `CIBW_ARCHS: arm64`;
   - MacOS 13: `CIBW_ARCHS: x86_64`;
   - Linux: `CIBW_ARCHS: auto64`;
   - Windows: `CIBW_ARCHS: AMD64`.
4. Run `cibuildwheel` from the modules/platforms/python/client:
   ```bash
   python -m cibuildwheel --output-dir wheels .
   ```

### Updating from an older version

To upgrade an existing package, use the following command:
```
pip install --upgrade pygridgain
```

To install the latest version of a package:

```
pip install pygridgain
```

To install a specific version:

```
pip install pygridgain==9.0.15
```

## Testing
*NB!* It is recommended installing `pygridgain` in development mode.
Refer to [this section](#from-sources) for instructions.

Remember to install test requirements:
```bash
$ pip install .[test]
```

### Run basic tests
Running tests themselves:
```bash
$ pytest
```

## File formatting, style checks, and lint
The project uses the following tools for maintaining clean and uniform code: isort, black, and ruff.
You can install the right version using the following command:
```bash
$ pip install .[format]
```

Before putting your code on review, you should probably run:
```bash
$ python tools/format_code.py
```

Then also run lint and style checker and fix every problem it finds: 
```bash
$ python tools/format_code.py --check
```
