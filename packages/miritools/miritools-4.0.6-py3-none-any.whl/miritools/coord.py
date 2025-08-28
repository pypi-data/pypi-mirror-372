"""
Coordinates related functions
"""

import numpy as np
import logging

LOG = logging.getLogger(__name__)

boresight_offset = dict(F560W=(0.08, 0.06), F770W=(0.00, 0.00), F1000W=(0.14, 0.62), F1130W=(-0.15, 0.59),
                        F1280W=(0.08, 0.70), F1500W=(0.36, 0.74), F1800W=(-0.39, 0.73), F2100W=(0.02, 0.27),
                        F2550WR=(0.27, 1.45), F2550W=(0.15, 0.55), F1065C=(0.60, 2.15), F1140C=(0.42, 1.56),
                        F1550C=(1.17, 1.47), F2300C=(-1.35, 2.11))


def filter_shift(input_filter, desired_filter):
    """
    Will transform the coordinates to make up for the boresight offset between the 2 filters

    :param str input_filter: Filter used to create the image
    :param str desired_filter: Desired filter for the updated position

    :return: coordinate shift in (col, row), 0-indexed
    :rtype: tuple(float, float)
    """

    input_shift = np.asarray(boresight_offset[input_filter])
    output_shift = np.asarray(boresight_offset[desired_filter])

    shift = tuple(output_shift - input_shift)

    return shift


def convert_filter_position(coord, input_filter, output_filter):
    """
    Given a colrow position obtained with a filter, will shift to predict what would be the position for output_filter

    :param coord: coordinates in (col, row) (0 indexed)
    :type coord: tuple(float, float)
    :param str input_filter:
    :param str output_filter:

    :return: coordinate in (col, row) for the new filter, 0-indexed
    :rtype: tuple(float, float)
    """

    shift = filter_shift(input_filter, output_filter)

    out_coord = np.asarray(coord) + np.asarray(shift)

    return tuple(out_coord)


def hms2dd(h, m, s):
    """
    Convert RA (ICRS) from Hours minutes seconds to decimal degrees

    :param float h: hour
    :param float m: minute
    :param float s: second

    :return: Right ascension in decimal degree
    :rtype: float
    """
    deg = (s / 3600 + m / 60 + h) * 15

    return deg


def dms2dd(d, m, s):
    """
    Convert DEC (ICRS) from degrees minutes seconds to decimal degrees

    :param float d: degree
    :param float m: minutes
    :param float s: seconds

    :return: Declination in decimal degree
    :rtype: float
    """

    dd = d + np.sign(d) * (m / 60 + s / 3600)
    return dd
