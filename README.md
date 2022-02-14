SPP 2086 Measurement Data Python Library
=====

Utilities for working with the JSON data format.

Installation
-----

    python -m pip install git+https://github.com/tgroche/spp2086-python.git

Alternatively download the repository and in the top directory execute

    python -m pip install .

Usage
----

The central element is the `MeasurementRecord` class. It can be used to create a representation in memory and write it to a conforming JSON file as well as vice versa. It also supports writing single series to external files as demonstrated by the test function `test_write_file_inplace_external`.
Reading files back into memory is demonstrated by `test_read_write_file`.

It is recommended to first build a valid header, which can be checked using `MeasurementRecord.validate_header()`, and then add sampling grids and data series.
