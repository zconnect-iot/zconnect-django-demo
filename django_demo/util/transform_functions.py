"""
This module defines transform functions that can be defined on an Demo
wiring mapping field. They all take a single value and return a single value.

The name of all function must be unique within this package.

If a transform function encounters an error, it should raise a TransformError
"""

# from django_demo.util.exceptions import TransformError

def invert(datapoint):
    """
    Take a value which could be a boolean or integer, or string, and invert it
    Always return 0 or 1
    """
    if isinstance(datapoint, str):
        lower = datapoint.lower()
        datapoint = (lower == 'true')

    return int(not bool(datapoint))
