# Version History

## 0.1.1
* Add CHANGELOG.md
* Update README.md
* Improve ZstdDecompressionReader.seek() method

## 0.1.0

* Add methods from_python(),  from_pandas(),  from_polars() to PGCryptWriter
* Add detect_oid function for generate oids from python types
* Add metadata_from_frame function
* Rename dtypes to pgtypes
* Change PGDataType to PGOid in pgtypes
* New __str__ and __repr__ output in PGCryptReader and PGCryptWriter

## 0.0.4

* Add support CopyByffer object as buffer

## 0.0.3

* Remove columns count from __str__ method

## 0.0.2

* Fix ZstdDecompressionReader.readall()
* Add docstring into __init__.py
* Improve docs
* Publish library to Pip

## 0.0.1

First version of the library pgcopy_parser
