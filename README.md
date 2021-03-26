# NAStools #

A python module for working with file formats commonly encountered in the field of observational/airborne atmospheric sciences. The project is still in its infancy but (limited) functionality is currently present in the module.


## What is Nastools? ##

Nastools provides a python package for dealing with common NASA file formats commonly encountered in the atmospheric science and instrumentation community.

Two common file formats are:

* [ICARTT File Format]
* [NASA Ames File Format]

NASA Ames format is now supported!

Note that only FFI = 1001 type-files are supported at this point.

[ICARTT File Format]: https://earthdata.nasa.gov/esdis/eso/standards-and-references/icartt-file-format
[NASA Ames File Format]: https://espoarchive.nasa.gov/content/Ames_Format_Specification_v20


## Quick Start Guide ##

The following should get you up and running quickly.

Issues/bugs/feature requests/etc can be [reported here](https://github.com/asobrien/NAStools/issues).


### Installation ###

Nastools are available from the [cheeseshop](https://pypi.python.org/pypi/NAStools/):

    pip install NAStools


### Using Nastools ###

Here are a few examples of how you can use nastools to help with your interactive analysis work.

#### Header Information ####

```python
import nastools

# Generate a Naspy object
h = nastools.Naspy(~/Desktop/sampleFile.nas)

# Get variable names
h.get_column_names()

# Get instrument info
print h.header.INSTRUMENT_INFO

# Get start time of file
startUtc = h.time.start_time()
print startUtc.isoformat()

# Get end time of file
endUtc = h.time.end_time()
print endUtc.isoformat()

# Total length of file
totalTime = endUtc - startUtc
print "**TOTAL FILE LENGTH**"
print "%s seconds" % totalTime.total_seconds()

# See all the header keys
print D.header.__dict__.keys()

# See all the header info in a (relatively) nice format
for key, val in h.header.__dict__.iteritems():
    print '%s: %s\n' % (key, val)
```
Generating a Naspy object is enough to start doing analysis.


#### Generate a Numpy Array ####

```python
import nastools
h = nastools.Naspy(~/Desktop/sampleFile.nas)

# Make a numpy array
arr = h.make_numpy()

# Make a masked array with missing values masked
arr = h.make_numpy(masked=True)
```

#### Generate a DataFrame ####

```python
import nastools
h = nastools.Naspy(~/Desktop/sampleFile.nas)

# Make a pandas.DataFrame
df = h.make_DataFrame()

# Make a pandas.DataFrame with integer index (not datetime)
df = h.make_DataFrame(datetime_asindex=False)
# rename 'DATETIME' field to 'DT'
df = df.rename(columns={'DATETIME':'DT'})
```

## VERSION HISTORY ##

* **0.1.0**: Initial release.
* **0.1.1**: Support for NASA Ames files added; custom variable names can be passed to both pandas.DataFrame and numpy.array objects.
* **0.1.2**: Added timezone localization to DataFrames; fixed bug preventing Datetime construction in DataFrames; fixed potential bug when automatically determining filetype.
* **0.2.0**: Adds option to use any column as datetime field (@maahn, #4); removes unused
    yamler.py source file (fixes #3); ownership info updated.
* **0.2.1**: Fixes incorrect spelling throughout (ICARRT -> ICARTT, fixes #7).















