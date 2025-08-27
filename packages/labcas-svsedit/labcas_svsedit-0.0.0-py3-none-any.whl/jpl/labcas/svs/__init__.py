# encoding: utf-8

'''JPL LabCAS SVS package.'''

import importlib.resources

__version__ = VERSION = importlib.resources.read_text(__package__, 'VERSION.txt').strip()
