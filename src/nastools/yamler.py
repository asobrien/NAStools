# yamler.py

# Yaml processing submodule

# Import the yaml
import yaml
def load_yaml(fname):
    """
    Loads a yaml file into the assigned variable:
    hdr = loadyaml(fin)
    
    hdr.keys() gives the dictionary
    """
    f = open(fname, 'r')
    hdr = yaml.load(f)
    f.close()
    return hdr
    
# make a Naspy header obj
# import _core
# Header

# this has to happen inside _core (I think) but how will it go
# process the empty header object
# or maybe this is a yaml header obj? 
hdict = load_yaml(fname)
for key, value in hdict.iteritems():
    # Do we need to worry about subdicts here?
    setattr(self, key, value)
    print keys, vals
    

# Process known fields

def PI(self, use_initials=False):
    piList = []
    for item in self.PI:
        string = ###
        piList.append(item['LAST_NAME'])
        