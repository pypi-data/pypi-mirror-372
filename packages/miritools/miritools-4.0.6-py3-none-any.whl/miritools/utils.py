"""
Misc functions that can't be sorted into another section
"""
import glob
import shutil
import sys
import time
from typing import List, Dict
from functools import wraps
import numpy as np
from astropy.io import fits
import os
import collections
import tabulate

import logging

from . import constants

LOG = logging.getLogger(__name__)


def list_files(pattern):
    """
    Retrieve a list of files following a pattern (using glob). Files are then sorted.

    Return an error if no files are found

    :param str pattern: a Regexp for Glob to list files

    :return list: List of files corresponding to pattern
    :rtype: list(str)
    """

    LOG.info(f"List files corresponding to {pattern}.")

    file_list = glob.glob(pattern, recursive=True)

    if not file_list:
        raise ValueError("'{}' has no match".format(pattern))

    file_list.sort()

    return file_list


def list_ordered_files(pattern: str, jpl=False) -> List[str]:
    """
    Retrieve a list of files following a pattern (using glob)
    then order the filenames w.r.t their OBS_DATE

    This function is usefull because a simple sort will place exp10 before exp1
    (since we don't have exp01 instead of exp1)

    Order the fits files by date. The first element of the list will be the first
    observation, the last will be the latest.

    WARNING:
    DATE_OBS format is assumed to be: yyyy-mm-dd
    TIME_OBS format is assumed to be: hh:mm:ss

    :param str pattern: a Regexp for Glob to list files
    :param bool jpl: If dealing with JPL files instead of standard datamodel

    :return list: file_list with elements ordered by DATE-OBS/TIME-OBS
    """

    file_list = list_files(pattern)

    tmp = []
    for filename in file_list:

        metadata = fits.getheader(filename)

        if jpl:
            metadata = correct_JPL_metadatas(metadata)

        # DATE_OBS format is assumed to be: yyyy-mm-dd
        # TIME_OBS format is assumed to be: hh:mm:ss
        time_fmt = "%Y-%m-%d %H:%M:%S.%f"

        time_str = "{} {}".format(metadata['DATE-OBS'], metadata['TIME-OBS'])

        if "." not in time_str:
            time_str += ".00"

        structime = time.strptime(time_str, time_fmt)

        # We shift by half the integration duration
        time_tmp = time.mktime(structime)
        tmp.append(time_tmp)

    ordering = np.argsort(tmp)

    # To sort it using the argsort output, we need a numpy array
    return list(np.array(file_list)[ordering])


def get_exp_time(metadata: Dict) -> float:
    """
    Return the start observation time of a given exposure

    We assume MIRI metadata format. We need DATE-OBS, TIME-OBS

    DATE-OBS format is assumed to be: yyyy-mm-dd
    TIME-OBS format is assumed to be: hh:mm:ss

    :param metadata:
    :return:
    """

    # .%f for a floating point number of seconds
    time_fmt = "%Y-%m-%d %H:%M:%S.%f"
    time_str = "{} {}".format(metadata['DATE-OBS'], metadata['TIME-OBS'])
    if "." not in time_str:
        time_str += ".00"
    structime = time.strptime(time_str, time_fmt)

    return time.mktime(structime)


def lambda_over_d_to_pixels(wavelength):
    """
    Given a wavelength, will output the size of Lambda/D in pixel for JWST MIRI

    :param float wavelength: wavelength in microns

    :return: size in pixels of lambda/D
    :rtype: float
    """
    radius_radians = wavelength * 1e-6 / constants.jwst_mirror_diameter
    radius_pixel = np.rad2deg(radius_radians) * 3600 / constants.pixel_size

    return radius_pixel


def timer(f):
    """
    Decorator to display time spent in the function

    :param f: Function to be decorated
    :return: decorated function
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        res = f(*args, **kwargs)
        end = time.perf_counter()
        print(f'{f.__name__} done in {end-start:.2f} s')
        return res
    return wrapper


def optimum_nbins(data):
    """
    Compute the optimum number of bins for a given dataset using the Freedman-Diaconis rule

    We assume the histogram will be between min and max

    source: https://stats.stackexchange.com/questions/798/calculating-optimal-number-of-bins-in-a-histogram

    :param list data: list of input data
    :return: optimum number of bins
    :rtype: int
    """
    q75, q25 = np.percentile(data, [75, 25])
    iqr = q75 - q25

    bin_width = 2 * iqr * len(data) ** (-1 / 3)
    nbins = (np.nanmax(data) - np.nanmin(data)) / bin_width

    return int(nbins)


def reorder_miri_input_folder(input_folder, dryrun=False, overwrite=True):
    """
    Take an input folder where everything is either at the root directory or in cryptic subfolders
    Some files, e.g. TA, will not be moved.

    Note that a bash script is created to cancel the move in case you made a mistake. Be carefull to not run the
    function twice or you might loose that backup script and struggle to retrieve the original structure (see
    the overwrite parameter for more info)

    Will create subfolders following the guidelines established for CAP104/501/502:
    * First folder level is the APT ID number
    * second layer split files given their obs_id, detector and filter used. Here are some examples of output:
        1028/obs4_IMA_F560W
        1028/obs5_IMA_F560W
        1028/obs6_IMA_F770W
        1028/obs6_IMA_F1000W
        1288/obs2_IMA_F1130W
        1288/obs2_IMA_F1500W
        1288/obs2_IMA_F770W
        1288/obs2_MRS_LONG
        1288/obs2_MRS_MEDIUM
        1288/obs2_MRS_SHORT
        1288/obs3_DARK

    :param str input_folder: input folder where all files are. Will be the base dir of the output structure
    :param bool dryrun: If true, only display how the file would have moved if not dryrun.
                        Warning: Destination folders will still be created
    :param bool overwrite: If True (by default it is), will not ask before overwriting the cancel script if it exists
    """
    files = list_files(os.path.join(input_folder, "**/*.fits"))

    new_paths = {}
    for file in files:

        new_path = miri_fancy_path(file)

        # Do nothing if the None was returned, because this file is considered not to be moved based on metadata.
        if new_path is None:
            continue

        new_full_path = os.path.join(input_folder, new_path)  # Append new path to original input folder

        new_paths[file] = new_full_path

    # Check file that are already correctly moved.
    for old, new in list(new_paths.items()):
        if old == new:
            del new_paths[old]

    nb_files = len(files)
    nb_moved = len(new_paths)
    if nb_moved == 0:
        LOG.info("No files to move.")
        return
    else:
        LOG.info(f"{nb_moved}/{nb_files} are going to be moved.")

    # Create bash script to move back files into original location if needed
    LOG.info("Creating backup script to cancel any moved file.")
    cancel_script = os.path.join(input_folder, "cancel_miri_reorder.sh")
    if os.path.isfile(cancel_script) and not overwrite:
        LOG.error(f"{os.path.relpath(cancel_script, input_folder)} already exist, "
                    f"and you requested not to overwrite in this case.")
        sys.exit()

    obj = open(cancel_script, "w")
    obj.write(f"#!/bin/bash\n")
    obj.write(f"# Script to cancel moves done by miricap.imager.utils.reorder_miri_input_folder\n\n")

    for old_path, new_path in new_paths.items():
        obj.write(f'mv "{os.path.relpath(new_path, input_folder)}"'
                  f' "{os.path.relpath(old_path, input_folder)}"\n')
    obj.close()

    LOG.debug(f"Dictionary of files to be moved: {new_paths}")

    if dryrun:
        movefunc = lambda src, dest: print(f"mv {src} {dest}")
    else:
        movefunc = shutil.move

    # Move file at the end, so that no file is moved in case there is a problem for one file.
    for file, new_full_path in new_paths.items():
        # Create destination directory if it doesn't exist
        dir, basename = os.path.split(new_full_path)
        if not os.path.isdir(dir):
            os.makedirs(dir)

        movefunc(file, new_full_path)

    LOG.info("File moved.")


def miri_fancy_path(filename):
    """
    Reading metadata, will come up with a better name and subfolder than the original cryptic name

    This only works for MIRI files. TA is treated separately. Unknown files or files that are not science files
    will return None

    Keyword used:
        OBSERVTN
        PROGRAM
        APERNAME
        FILTER or BAND
        DETECTOR
        SUBARRAY
        [optional] TEMPLATE

    :param str filename:
    :return: New path based on header keywords
    """

    try:
        with fits.open(filename) as hdulist:
            header = hdulist[0].header
    except OSError:
        LOG.error(f"Problem opening {filename}")
        raise

    obsid = int(header["OBSERVTN"])
    program = int(header["PROGRAM"])

    obs_description = [f"obs{obsid}"]

    detector = header["DETECTOR"]  # e.g. MIRIFUSHORT
    subarray = header["SUBARRAY"]

    # Move TA separately, they can come from another instrument (but haven't tested that for lack of example)
    apername = header["APERNAME"]
    if "TA" in apername or not apername.startswith("MIRI"):
        obs_description.append("TA")
    else:
        # Only check all this if current file is not TA
        try:
            template = header["TEMPLATE"].lower()
        except KeyError:
            template = ""

        if "dark" in template:
            # Dark Image
            obs_description.append("DARK")
        else:
            # Actual image
            if "MIRIFU" in detector:
                obs_description.append("MRS")

                band = header["BAND"]
                obs_description.append(band)
            else:
                filter_name = header["FILTER"]

                if "MASK" in subarray:
                    obs_description.append("COR")
                elif filter_name == "P750L":
                    obs_description.append("LRS")
                else:
                    obs_description.append("IMA")

                obs_description.append(filter_name)

    program_folder = f"{program}"
    folder_name = "_".join(obs_description)

    basename = os.path.basename(filename)
    new_path = os.path.join(program_folder, folder_name, basename)

    return new_path


def assert_list_dict_equal(input_list, ref_list):
    """
    Assert that the two input lists of dictionaries are equal by asserting that
      1. list are same length
      2. running element-wise comparison of dictionaries in the two lists

    :param list input_list: input list of dictionaries
    :param list ref_list: reference list of dictionaries
    """

    assert len(input_list) == len(ref_list), "List have different sizes"

    for (d1, d2) in zip(input_list, ref_list):
        assert_dict_equal(d1, d2)


def assert_dict_equal(input_dict, dict_ref):
    """
    Assert if two input dictionaries are equal. If not, display the differences.

    :param dict input_dict: Input dictionary
    :param dict dict_ref: Reference dictionary
    """

    (is_equal, msg) = compare_dict(input_dict, dict_ref)

    assert is_equal, msg


def compare_dict(input_dict, dict_ref, msg=None, prefix=None):
    """
    Compare 2 dictionaries to determine if they are the same. Will return an error message explaining the differences.

    :param dict input_dict: Input dictionary
    :param dict dict_ref: Reference dictionary

    Warning: All other parameters are internal (for recursivity) and must NOT be used

    :return: if dict are equal and error message associated with it
    :rtype: (bool, msg)
    """

    is_equal = True

    if not msg:
        msg = ""

    keys1 = set(input_dict.keys())
    keys2 = set(dict_ref.keys())

    d1_prefix = "input_dict"
    d2_prefix = "dict_ref"
    if prefix:
        d1_prefix += prefix
        d2_prefix += prefix

    common_keys = keys1.intersection(keys2)

    # Keys present in keys1 not present in keys2
    new_keys1 = keys1.difference(keys2)
    if len(new_keys1) != 0:
        is_equal = False
        msg += "Keys exclusive to {}:\n".format(d1_prefix)
        for key in new_keys1:
            msg += "\t{}[{}] = {}\n".format(d1_prefix, key, input_dict[key])

    # Keys present in keys2 not present in keys1
    new_keys2 = keys2.difference(keys1)
    if len(new_keys2) != 0:
        is_equal = False
        msg += "Keys exclusive to {}:\n".format(d2_prefix)
        for key in new_keys2:
            msg += "\t{}[{}] = {}\n".format(d2_prefix, key, dict_ref[key])

    # Common keys
    for key in common_keys:
        value1 = input_dict[key]
        value2 = dict_ref[key]
        if isinstance(value1, dict):
            new_prefix = prefix if prefix else ""
            new_prefix += "[{}]".format(key)
            (value_equal, tmp_msg) = compare_dict(value1, value2, prefix=new_prefix)
            if not value_equal:
                is_equal = False
            msg += tmp_msg
        elif value1 != value2:
            is_equal = False
            msg += "Difference for:\n"
            msg += "\t{}[{}] = {}\n".format(d1_prefix, key, value1)
            msg += "\t{}[{}] = {}\n".format(d2_prefix, key, value2)

    return is_equal, msg


def update_dict(d, u):
    """
    Recursively merge or update dict-like objects.
    i.e, change a value to a key that already exists or
    add a (key, value) that did not previously existed

    source: https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth

    :param dict d: Original dictionnary
    :param dict u: dictionnary of updates to apply to 'd'
    :return dict d: Return updated version of 'd'
    """

    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update_dict(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def init_log(log="miritools.log", stdout_loglevel="INFO", file_loglevel="DEBUG", extra_config=None):
    """

    :param str log: filename where to store logs. By default "miritools.log"
    :param str stdout_loglevel: log level for standard output (ERROR, WARNING, INFO, DEBUG)
    :param str file_loglevel: log level for log file (ERROR, WARNING, INFO, DEBUG)
    :param dict extra_config: [optional] Set of extra properties to be added to the dict_config for logging
    :return:
    :rtype:
    """

    import logging.config

    log_config = {
        "version": 1,
        "formatters":
            {
                "form01":
                    {
                        "format": "%(asctime)s %(levelname)-8s %(message)s",
                        "datefmt": "%H:%M:%S"
                    },
                "form02":
                    {
                        "format": "%(asctime)s [%(processName)s/%(name)s] %(levelname)s - %(message)s",
                        "datefmt": "%H:%M:%S"
                    },
            },
        "handlers":
            {
                "console":
                    {
                        "class": "logging.StreamHandler",
                        "formatter": "form01",
                        "level": stdout_loglevel,
                        "stream": "ext://sys.stdout",
                    },
                "file":
                    {
                        "class": "logging.FileHandler",
                        "formatter": "form02",
                        "level": file_loglevel,
                        "filename": log,
                        "mode": "w",  # Overwrite file if it exists
                    },
            },
        "loggers":
            {
                "":
                    {
                        "level": "NOTSET",
                        "handlers": ["console", "file"],
                    },
            },
        "disable_existing_loggers": False,
    }

    if extra_config is not None:
        log_config = update_dict(log_config, extra_config)

    logging.config.dictConfig(log_config)


def dump_dict(input, indent_level=0):
    """
    Will dump the input dict as a string to be printed or written to file.
    It will display nicely the dictionnary with the same format as configobj

    :param dict input: Input dictionnary
    :return: Input dictionnary as a string (On multiple lines)
    :rtype: str

    """
    INDENT_STR = "  "
    str = ""
    for (k,v) in input.items():


        if isinstance(v, dict):
            str += INDENT_STR * indent_level
            str += "[" * (indent_level + 1)
            str += f"{k}"
            str += "]" * (indent_level + 1)
            str += "\n"

            str += dump_dict(v, indent_level=indent_level+1)
            str += "\n"
        else:
            str += INDENT_STR * indent_level
            str += f"{k} = {v}\n"

    return str


def inspect_datamodel_schema(model):
    """
    The input objet must be a datamodel, e.g. miri.datamodels.miri_psf_models.MiriImagingPointSpreadFunctionModel()

    :param jwst.datamodels.JwstDataModel model: object datamodel for any of the MIRI datamodels
    :return: str
    """

    table = __recursive_inspect(model.schema)

    # sort all lines (except the first one)
    new_table = table[1:]
    new_table.sort()

    new_table.insert(0, table[0])

    string_report = tabulate.tabulate(table, headers="firstrow")

    return string_report


def __recursive_inspect(schema, key=""):
    columns = ["fits_keyword", "type", "title"]
    table = []

    # Add the header if it's the main call
    if not key:
        tmp = ["Keyword"]
        tmp.extend(columns)
        table.append(tmp)

    if "fits_keyword" in schema:
        tmp = [key.replace("properties.", "")]

        for k in columns:
            tmp.append(schema[k])

        table.append(tmp)
    else:
        for (k, v) in schema.items():
            if not isinstance(v, dict):
                continue

            if not key:
                new_key = k
            else:
                new_key = f"{key}.{k}"

            table.extend(__recursive_inspect(v, key=new_key))

    return table