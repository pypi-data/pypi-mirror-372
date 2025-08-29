"""
SQAPI - A python package that simplifies interactions with the SQUIDLE+ API.

It can be used to integrate automated labelling from machine learning algorithms 
and plenty other cool things.
"""

__version__ = "0.60"
__author__ = "Greybits Engineering"
__email__ = "support@greybits.com.au"

# Make version easily accessible
from sqapi.api import *
from sqapi.media import *
from sqapi.annotate import *
from sqapi.helpers import *