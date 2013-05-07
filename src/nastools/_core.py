# NAS Tool

# we need to clean up ict module, but the core functionality is there

# required modules
# Module to process ICARTT data
import numpy as np
import gzip
import os
import datetime
import pandas
import bz2
import warnings
# import copy
import numpy.lib.recfunctions as rfn  # need array append function
import struct

class Fifo(object):
    """File input / File output handler class."""
    def __init__(self, filename):
        self.filename = filename
        # self.filetype_warnings() # issue any warnings
        return None
        
    def get_filetype(self):
        """Returns a string of filetype.
        
        RETURNS
        -------
        ext : string
            File-extension of Naspy object. Note that 'gz' are returned as 'gzip'.
            
        """
        fname = self.filename
        ext = os.path.splitext(fname)[-1].lower().lstrip('.') # force lower case
        if ext == 'gz':
            ext = 'gzip'
        return ext
            
    def open_file(self):
        """Generates fileObj based on extension.
        
        This creates an open fileObj, it is up to you to close it when done with it.
        """
        fname = self.filename
        
        ext = os.path.splitext(fname)[-1].lower() # force lower case
        # this is returning text file! or not working
        if ext in ['.gz','.gzip']:
            f = gzip.GzipFile(filename=fname, mode='rb')
        elif ext in ('.bz2'):
            f = bz2.BZ2File(fname, 'rU')
        else:
            f = open(fname, 'rU')
        return f
        
    def filetype_warnings(self):
        # Need to issue warning re .gz file type
        warningMessage = "Gzipped filetypes are not fully supported.\nHeader information is available through the header instance, however generating numpy arrays from gzipped is not currently possible. Generating pandas.DataFrames IS SUPPORTED."
        
        fname = self.filename
        ext = os.path.splitext(fname)[-1].lower() # force lower case
        if ext in ['.gz','.gzip']:
            warnings.warn(warningMessage)
        else:
            return None

    def gzipFileSize(self):
        """return UNCOMPRESSED filesize of a gzipped file.
        
        source: http://code.activestate.com/lists/python-list/245777/
        """
        fo = open(self.filename, 'rb')
        fo.seek(-4, 2)
        r = fo.read()
        fo.close()
        return struct.unpack('<I', r)[0]
        
        
class Naspy(object):
    "Initializes a Naspy object"
    def __init__(self, fname):
        self._fileAbsPath_ = os.path.abspath(fname) # full path to file
        self._file = Fifo(self._fileAbsPath_) # File object instance
        self.header = Header(self) # This needs to be passed into Header, so we can 
                                   # derive attrs
        self.time = Time(self)  # Get time functionality
        # Issue gzip warning:
        Fifo(self._fileAbsPath_).filetype_warnings()
        
        return None
        
    def make_numpy(self, masked=False, missing_values='auto'):
        """Generates a numpy ndarray.
        
        PARAMETERS
        ----------
        masked : bool, default False
            Species whether to return a masked array; must be True to convert missing 
            values to nans in the returned array.
        missing_values : 'auto' or list, default 'auto'
            A list of strings specifying additional field names in the header file 
            (e.g. 'LLOD_FLAG') which indicate missing values. The default behavior is 
            'auto' which automatically searches for 'LLOD_FLAG' and 'ULOD_FLAG' fields in 
            the header. Note that the missing data flags for the dependent variables 
            (e.g. -99999) do not need to be specified.
            
        """
        # Get variable names
        names = [ self.header.INDEPENDENT_VARIABLE['NAME'] ]
        for i in range(len(self.header.DEPENDENT_VARIABLE)):
            names.append(self.header.DEPENDENT_VARIABLE[i]['NAME'])
        
        # Get a dictionary of missingVals on a per column basis
        if missing_values == 'auto':
            missingVals = self.missing_values()
        else:
            missingVals = self.missing_values(missing_values)
        
        # Read the lines into numpy object
        arr = np.genfromtxt(
                    self._fileAbsPath_,
                    delimiter = ',',  # Comma seperated (ICT/AMES style?),
                    names = names,
                    skip_header = self.header.HEADER_LINES,
                    missing_values = missingVals,
                    usemask=masked,
                    dtype = None,
                    case_sensitive = False,
                    unpack=True
                    )
        
        # KNOWN DEFECT: can't append datetime64 to an existing array using:
        #   numpy.lib.recfunctions.append_fields
        #  fixed in Numpy 1.7.0 
        #  (see: http://projects.scipy.org/numpy/ticket/1912)
        #  (github: https://github.com/numpy/numpy/issues/2505)
        
        # Datetime fields are mangled in numpy 1.6 using the following methods
        # I think this is fixed in NP 1.7, so let's hold off until we use that
        #  see (http://bit.ly/12HjWG6) for information on behavioral differences between
        #   versions 1.6 and 1.7
        
        # Quick fix, add new field, then convert
            #  DT = (arr[arr.dtype.names[0]])
            #  arr = rfn.append_fields(arr, names='DATETIME', data=DT, usemask=False)
            #  
            #  if datetime: # generate a datetime object column
            #      arr['DATETIME'] = (
            #          np.timedelta64(arr['DATETIME']*1E6) + 
            #          np.datetime64(self.header.START_UTC.isoformat())).astype('datetime64')
            #      # Need to operate on primary variable
            #      # This get our time:
            #      # np.timedelta64(foo*1E6)+np.datetime64(GG.header.START_UTC.isoformat())s
            #  # arr = np.append(arr, DT)
            #  appArr = numpy.lib.recfunctions.append_fields(arr,
            #     names ='DATETIME', data=DT, 
            #     usemask=False, asrecarray=False)
        
        return arr
    
    
    def make_DataFrame(self, case_sensitive='upper', convert_missing=True, 
                        make_datetime=True, datetime_asindex=True, drop_datetime=True,
                        missing_values='auto'):
        """Generates a pandas.DataFrame from a Naspy object.
        
        PARAMETERS
        ----------
        case_sensitive : string or bool, default 'upper'
            Formatting option of columns names; choices are 'upper' (default), 'lower', or
            'as-is' in addition to True or False. With no format specified, column names 
            will be returned in upper case; 'as-is' or True returns variables in the case 
            as they are specified in the file.
        convert_missing : bool, default True
        make_datetime : bool, default True
        datetime_asindex : bool, default True
        drop_datetime: bool, default True
        missing_values : 'auto' or list, default 'auto'
            A list of strings specifying additional field names in the header file 
            (e.g. 'LLOD_FLAG') which indicate missing values. The default behavior is 
            'auto' which automatically searches for 'LLOD_FLAG' and 'ULOD_FLAG' fields in 
            the header. Note that the missing data flags for the dependent variables 
            (e.g. -99999) do not need to be specified.
        compression : {'auto', 'gzip', 'bz2', None}, default 'auto'
            For on-the-fly decompression of on-disk data; 'auto' will try and detect 
            filetype based on extension. Use other options to manually override 'auto'.
        
        
        """
        # END EXAMPLES:
        # Rename datetime to dt:
        # df = df.rename_axis({'DATETIME':'DT'})
        
        # what are the index options
        
        # Compressed file?
        ext = Fifo(self._fileAbsPath_).get_filetype()
        print ext
        if ext not in ['gzip', 'bz2']:
            ext = None
        
        df = pandas.io.parsers.read_table(
                 self._fileAbsPath_, 
                 skiprows = self.header.HEADER_LINES, 
                 delimiter = ',', 
                 names = self.get_column_names(case_sensitive),
                 dtype = np.float64, # Allow for nans
                 compression = ext
                 )
        
        if convert_missing:
             df = self.dataframe_nans(df, missing_values)
         
         # make datetime object
        # dt = []
#         for utcSecs in df[df.columns[0]].values:
#              dt.append(datetime.timedelta(0, int(utcSecs))+self.header.START_UTC)
#         df['foo'] = pandas.Series(dt)
         
        # Can we do the same thing with numpy methods, yes and it's prob faster
        
        if make_datetime:
            DATETIME = 'DATETIME'
            df[DATETIME] = ( np.timedelta64(df[df.columns[0]]*1E6) + 
                             np.datetime64(self.header.START_UTC.isoformat()) )
            if datetime_asindex:
                df = df.set_index(DATETIME, drop=drop_datetime)
        
        # reindex into DATETIME
        # df = df.reindex(index=df['DATETIME'])
        
         # First make a numpy array, not masked!
         # arr = self.make_numpy()
#          df = pandas.DataFrame(data=array)
        
        return df
    
    
    def get_column_names(self, case_sensitive='upper'):
        """Returns a list of column names from a Naspy object.
        
        PARAMETERS
        ----------
        case_sensitive : string or bool, default 'upper'
            Formatting option of columns names; choices are 'upper' (default), 'lower', or
            'as-is' in addition to True or False. With no format specified, column names 
            will be returned in upper case; 'as-is' or True returns variables in the case 
            as they are specified in the file.
            
        """
        names = [ self.header.INDEPENDENT_VARIABLE['NAME'] ]
        for i in range(len(self.header.DEPENDENT_VARIABLE)):
            names.append(self.header.DEPENDENT_VARIABLE[i]['NAME'])
        
        if case_sensitive in ['upper', False]:
            names = [name.upper() for name in names]
        elif case_sensitive == 'lower':
            names = [name.lower() for name in names]
        elif case_sensitive in ['as-is', True]:
            pass
        else:
            raise ValueError("case_sensitive option '%s' is undefined." % case_sensitive)
        
        return names
    
    def dataframe_nans(self, df, missing_values='auto'):
        """missing_values is a dictionary.
        """
        # MAKE SURE COLUMN IS A FLOAT IF WE WANT TO INSERT NANS
        
        # Get a dictionary of missingVals on a per column basis
        if missing_values == 'auto':
            missingVals = self.missing_values()
        else:
            missingVals = self.missing_values(missing_values)
        
        for key, val in missingVals.iteritems():
            df[df.columns[key]] = df[df.columns[key]].replace(val, np.nan)
            
        # need to replace each column missing values, using missingVal dict
        # MAKE SURE COLUMN IS A FLOAT IF WE WANT TO INSERT NANS
        #  how do we do this... nans are not supported for int currentls.. so?
        return df
    
    def missing_values(self, flags=['LLOD_FLAG', 'ULOD_FLAG']):
        """Generates a dictionary of missing values on a per column basis.
        Option: flags; a list of strings with attribute names of missing data flags
                        that reside inside in a numpy object. The default flags
                        should work in most cases, and if they don't exist they are
                        ignored gracefully.
                        
        Returns: missingVals (dict); a per column list of missing values, with index
                                    value as key (int)
        
        key : string
            'int' or 'names'; 'int' returns integer key and 'names' returns column names.
        """
        # Make sure attributes exist
        otherFlags = []
        [flag.upper() for flag in flags]  # Ensure uppercase
        for flag in flags:
            try:
                otherFlags.append(str(getattr(self.header, flag)))
            except AttributeError:
                pass # Attribute doesn't exist
        
        # get column names
        # names = self.get_column_names()
        
        # Column specific missing values
        missingVals = {} # Time column is never missing!
        for i, flag in enumerate(self.header.MISSING_DATA_FLAGS):
            # if key == 'names':
            key = i+1
            # elif key == 'int':
                # key = i+1
            missingVals[key] = str(flag).strip()
        
        # append missing flags to each column
        for key, value in missingVals.iteritems():
            j = list(otherFlags) # Copy list
            j.insert(0, value) # insert default missing flag first
            missingVals[key] = j # Reassign
        
        return missingVals
    
    def __repr__(self):
        return "NASA Ames Data File (FFI = %i)\n%s" % (self.header.FFI,
            self.header.FILENAME)

class Header(object):
    "Generates header information for a Naspy object, requires Naspy object."
    def __init__(self, Naspy):
        
        fname = Naspy._fileAbsPath_
        # fname = parent._fileAbsPath_
#         ext = os.path.splitext(fname)[1]
#         if ext.lower() in ('.gz'):
#             f = gzip.open(fname)
#         else:
#             f = open(fname, 'rU')
        self._fileObj_ = Naspy._file.open_file() # Attach fileObject
        self._fileAbsPath_ = os.path.abspath(fname) # full path to file
        self.FILENAME = os.path.split(fname)[1]
        self._parse_header_() # parse the header
        self._parse_normal_comments_() # additional comments
        self._fileObj_.close()  # Make sure the file is when done
        # self.fname = fname
        # self.time = time(fname) # initialize; but I need to inherit!
        return None
        
    
    def _parse_header_(self):
        f = self._fileObj_
        # f.seek(0) # Ensure at start of file

        self.HEADER_LINES, self.FFI = map(int, f.readline().split(','))
        self.PI = f.readline().strip()
        self.ORGANIZATION = f.readline().strip()
        self.DATA_DESCRIPTION = f.readline().strip()
        self.MISSION = f.readline().strip()
        self.FILE_VOL_NO, self.NO_VOL = map(int, f.readline().split(','))

        i = map(int, f.readline().split(','))
        self.START_UTC = datetime.datetime(i[0],i[1],i[2]) # UTC date when data begin
        self.REV_UTC =  datetime.date(i[3],i[4],i[5]) # UTC date of data red or rev

        self.DATA_INTERVAL = float(f.readline())
        
        # Generate a dictionary for INDEPENDENT_VARIABLE
        j = f.readline().strip().split(',') # Read Indepent_Variable line
        for k in range(len(j),3):  # Ensure all fields are filled
            try:
                j[k] = None
            except IndexError:
                j.append(None)
        self.INDEPENDENT_VARIABLE = {'NAME':j[0], 'UNITS':j[1], 'DESC':j[2]}  
        
        self.TOTAL_NUM_VARIABLES = int(f.readline().strip())+1
        self.SCALE_FACTORS = self.SCALE_FACTORS = map(float, f.readline().split(','))
        # self.MISSING_DATA_FLAGS = map(float, f.readline().split(','))
        self.MISSING_DATA_FLAGS = f.readline().strip().replace(" ","").split(',')

        # Create a dictionary for dependent variables
        DEP_VAR = []
        for i in range(1,self.TOTAL_NUM_VARIABLES):
            j = f.readline().strip().split(',')
            for k in range(len(j),3):  # Ensure all fields are filled
                try:
                    j[k] = None
                except IndexError:
                    j.append(None)
            DEP_VAR.append({'NAME':j[0], 'UNITS':j[1], 'DESC':j[2]})
        self.DEPENDENT_VARIABLE = DEP_VAR

        self.SPECIAL_COMMENT_LINES = int(f.readline().strip())

        SPECIAL_COMMENTS = []
        for i in range(self.SPECIAL_COMMENT_LINES):
            SPECIAL_COMMENTS.append(f.readline().strip())
        self.SPECIAL_COMMENTS = SPECIAL_COMMENTS

        self.NORMAL_COMMENT_LINES = int(f.readline().strip())

        NORMAL_COMMENTS = []
        for i in range(self.NORMAL_COMMENT_LINES):
            NORMAL_COMMENTS.append(f.readline().strip())
        self.NORMAL_COMMENTS = NORMAL_COMMENTS

        return None


    def _parse_normal_comments_(self):
        for i in self.NORMAL_COMMENTS:
            comment = i.split(':',1)
            if len(comment) == 2:
                setattr(self, comment[0].upper().strip(), comment[1].strip())
        return None
    
    ### FUNCTIONS TO WORK Naspy object
    
    def contact_info(self):
        print """
        PRIMARY INVESTIGATOR(S)
        ----------------------- 
        %s
        
        AFFILIATION
        ----------- 
        %s
        
        CONTACT INFO
        ------------
        %s
        """ % (self.PI, self.ORGANIZATION, self.PI_CONTACT_INFO)
        return None

    def data_description(self):
        fileStart = self.START_UTC
            

class Time(object):  # I don't know how to inherit properly here!
    """All time based functions reside here."""
    def __init__(self, parent):
        self._fname = parent._fileAbsPath_
        self._START_UTC = parent.header.START_UTC
        self._HEADER_LINES = parent.header.HEADER_LINES
        
        return None
     
    def start_time(self):
        """Returns a datetime object of first datapoint."""
        startDate = self._START_UTC
        # Read the first timestamp
        # f = open(self._fname)
#         lines = []
#         for i in range(self._HEADER_LINES):
#             lines.append(f.readline())
        f = Fifo(self._fname).open_file()
        firstDataLine = f.readline()
        startOffset = datetime.timedelta(0, int(firstDataLine.split(',')[0]))
        startTime = startDate + startOffset
        f.close()
        return startTime
    
    # How to read last line in file?
    """Returns datetime object of last datapoint."""    
    def end_time(self):
        startDate = self._START_UTC
        # f = open(self._fname)
#         lines = []
#         for i in range(self._HEADER_LINES):
#             lines.append(f.readline())
        
        # seek from end not supported for gzip need to fix!
        # what about bz2
        f = Fifo(self._fname).open_file()
        firstDataLine = f.readline()
        
        # Can't read backwards in a gzip file, so:
        if Fifo(self._fname).get_filetype() == 'gzip':
            fsize = Fifo(self._fname).gzipFileSize()
            f.seek((fsize-fsize/20))
        else:
            f.seek(-len(firstDataLine)*10, 2)
        lastLine = f.readlines()[-1]
        endOffset = datetime.timedelta(0, int(lastLine.split(',')[0]))
        endTime = startDate + endOffset
        f.close()
        return endTime
        

#

# EOF
          
    