# NASPY -- NASA Data File Tools #


## What is/are Naspy & nastools? ##

Nastools provides a python package for dealing with common NASA file formats commonly encountered in the atmospheric science and instrumentation community.

Two common file formats are:

* ICARRT File Format
* NASA Ames File Format (not yet supported)


Currently NASA Ames File Format is not yet supported. It is similar to the ICARTT File format, yet its implementation into this toolbox is still under development. 

Note that only FFI = 1001 type-files are supported at this point.

## Quick Start Guide ##

The following should get you up and running quickly:

### Installation ###

Nastools are available from the cheeseshop:

    command for pip installation instructions here
    
Any other ways to install go here.

### Using Nastools ###

Here are a few examples of how you can use nastools to help with your interactive analysis work.

#### Header Information ####

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
    
Generating a Naspy object is enough to start doing analysis.


#### Generate a Numpy Array ####

    import nastools
    h = nastools.Naspy(~/Desktop/sampleFile.nas)
    
    # Make a numpy array
    arr = h.make_numpy()
    
    # Make a masked array with missing values masked
    arr = h.make_numpy(masked=True)
    

#### Generate a DataFrame ####

    import nastools
    h = nastools.Naspy(~/Desktop/sampleFile.nas)
    
    # Make a pandas.DataFrame
    df = h.make_DataFrame()
    
    # Make a pandas.DataFrame with integer index (not datetime)
    df = h.make_DataFrame(datetime_asindex=False)
    # rename 'DATETIME' field to 'DT'
    df = df.rename(columns={'DATETIME':'DT'})
    
    
    















