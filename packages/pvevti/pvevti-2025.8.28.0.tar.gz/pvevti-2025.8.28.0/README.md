# PVE-VTI Utility Package

**pvevti** is a pip-installable package intended to provide easy access to a suite of tools and enable accelerated analysis and modification of CSV files. The package is developed and maintained by the Vehicle Thermodynamics and Integration team under Product Validation Engineering at DTNA.

## Installation

To install **pvevti**, ensure `pip` is installed. `pip` is installed by default with any modern python installation. To check installation, enter `pip list`; if `pip` is installed, a list of packages installed to the local machine should be printed.

With `pip` verified to be functioning, simply enter `pip install pvevti`. A network connection is required to pull the files when installing or updating the package. 

To update **pvevti**, enter `pip install pvevti --upgrade`. If you believe a dependency is not being met, **pvevti** is improperly installed, or source files were altered, force a reinstall with `pip install pvevti --upgrade --force-reinstall`. This starts a lengthy process of each dependency's reinstallation - be ready!

To check if **pvevti** is installed, simply attempt to import the package in a python CLI or script. The version can be extracted by checking the package's `__version__` 'dunder' variable.

## Usage

**pvevti** is composed of a few modules:
 - **csvutil**: Utilities associated with CSV manipulation, loading, and saving.
 - **pdfutil**: Utilities associated with PDF creation, management, and saving. 
 - **jsonutil**: Utilities associated with JSON reading and management.
 - **genutil**: Utilities associated with packaging and managing data, manipulating and extracting properties, and all pandas DataFrame manipulation (including conversions, filters, and GPS management).
 - **mf4util**: Utilities associated with ASAM's MDF/MF4 file architecture; selective loading, filtering, and metadata acquisition.

The package is documented, in both source code and docstring formats. Most input arguments are typechecked, and safety rails exist to minimize the number of uncaught errors in a given process.

As with any package, use `pip uninstall pvevti` to remove the package and its dependencies. 

It is suggested to only import the modules you need; for example, instead of `import pvevti` a user who only needs the general utilities should run `import pvevti.genutil as gu`. This increases semantic legibility and decreases import time.

A select few utilities require internet connection to download basemaps as a part of the PDF creation process.

## Reference

For reference, please refer to [`docs.md`](docs.md). Examples of usage are found at the last section of the docs markdown file.