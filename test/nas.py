import os

import nastools

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

h = nastools.Naspy(os.path.join(THIS_DIR, './data/FFI-1001-a.prn'))

def test_column_names():
    cols = h.get_column_names()
    assert 'PRESSURE' in cols
    assert 'TOTAL CONCENTRATION' in cols
    assert 'TEMPERATURE' in cols

def test_header_ffi():
    assert h.header.FFI == 1001

