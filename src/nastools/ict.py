# ICARTT TOOLS

import datetime

# Functions for working with ICARTT files

# TODO: create similar to parse NAS header; there are a few subtle differences between the NAS and ICT, so a seperate nas function is best
# Operates on a Naspy.header object
def parse_header(self):
    """Parses an ICT header and returns a naspy.header object. """
    # get the filetype and specify the seperator
    
    f = self._fileObj_
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
            j.append("None")
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
                j.append("None")  # must be a string
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
    
    if len(NORMAL_COMMENTS) != 0:
        parse_normal_comments(self)
    
    # Get column variables from last line of file
    COL_VARS = NORMAL_COMMENTS[-1].strip().split(',')  # last column line
    if len(COL_VARS) == self.TOTAL_NUM_VARIABLES:
        self.COLUMN_VARIABLES = COL_VARS
        self.NORMAL_COMMENTS.pop() # pop off the variable names, since they're here
    
    return None


def parse_normal_comments(self):
    for i in self.NORMAL_COMMENTS:
        comment = i.split(':',1)
        if len(comment) == 2:
            setattr(self, comment[0].upper().strip(), comment[1].strip())
    return None

