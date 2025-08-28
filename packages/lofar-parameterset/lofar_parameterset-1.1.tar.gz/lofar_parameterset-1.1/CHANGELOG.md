Version 1.0
===========

**Release date: 2025-08-25**

This is the initial release of the python package `lofar-parameterset`. The implementation is identical to [parameterset.py](https://git.astron.nl/tmss/libraries/pycommon/-/blob/master/tmss_pycommon/parameterset.py?ref_type=heads) in [tmss_pycommon](https://git.astron.nl/tmss/libraries/pycommon/). The package will be available on [PyPI](https://pypi.org/project/lofar-parameterset/) and its documentation on [ReadTheDocs](https://lofar-python-parameterset.readthedocs.io/en/latest/).


Version 1.1
===========

**Release date: 2025-08-27**

This release adds some methods to the `lofar-parameterset` package that exist in the original LOFAR `ParameterSet` implementation, but were missing in this package. It is an extension of the existing API, and is therefore backward compatible. Also, some bugs were fixed.

* Added static method `fromFile`
* Added methods `getInt`, `getDouble`, `getBool`, and `getBoolVector`
* Fixed a bug in `makeSubset`, which was missing the optional `prefix` argument
* Warn on the use of `expandable` argument in the `get*Vector` methods
