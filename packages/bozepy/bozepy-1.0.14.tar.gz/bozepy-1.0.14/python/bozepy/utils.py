import os
import numpy as np

def datadir():
    """ Return the package data directory """
    fil = os.path.abspath(__file__)
    codedir = os.path.dirname(fil)
    datadir = codedir+'/data/'
    return datadir
