"""
Functions to read FITS files at various levels

All functions should return a time list, cube MaskedArray and list of metadata dict for each slice.
"""

import tabulate
import numpy as np
from astropy.io import fits

from . import utils
from . import mask as mk

import logging
LOG = logging.getLogger(__name__)


def MIRI_exposures(filenames, exclude_from_mask=None, flag_negative=True):
    """
    Read _cal or _rates MIRI file and return list of images/metadata corresponding to each file
    Each file must have only one image per exposures (use MIRI_rateints otherwise)

    Invalid and negative fluxes are masked (with a warning)

    All mask are combined to make sure if one pixels is selected that it's visible for all slices

    There's an exception if we have only one exposure. Instead of having an extra dimension with 1 value only,
    we simply return the image. Idem, instead of a list of a single dictionnary, we return the dictionnary
    (intended for reference image)

    :param filenames: List of filenames
    :param exclude_from_mask: In case you want to include pixel types that are normally excluded.
            Specify the list of pixel status you want to include, as a list
            - 1    : dead pixel
            - 2    : hot pixel
            - 4    : noisy pixel
            - 8    : high saturation
            - 16   : pixel saturation mask
            - 32   : cosmic ray
            - 64   : noise spike downward
            - 128  : a noise spike upward
            - 256  : Looks like a negative cosmic ray (the frames after the high are offset downward).
            - 512  : No electronic non-linearity correction exists (or has high errors)
            - 1024 : Ramp contains data outside of electronic linearity correction range.
            - 2048 : No mean dark correction exists for pixel.
    :return: array of middle time for each exposure, Cube image (nb_exp, y, x), metadata for each exposure as a dict
    """
    LOG.info("Reading MIRI exposures")

    if isinstance(filenames, str):
        filenames = [filenames]

    images = []
    masks = []
    metadatas = []
    times = []
    for file in filenames:
        LOG.debug(f"Reading file {file}")
        hdulist = fits.open(file, memmap=False)  #

        metadata = hdulist[0].header
        raw_image = hdulist['SCI'].data  # DN/s

        if raw_image.ndim != 2:
            raise ValueError(f"{file} doesn't seem to be MIRI level 2 image data. data shape should have 2 dimensions, "
                             f"got {raw_image.ndim} ({raw_image.shape}).")

        # Create a masked array
        try:
            mask = hdulist['DQ'].data
        except KeyError:
            # MIRISim don't create any DQ image, so it's possible that
            # real raw data don't have it, and only modified ramps have DQ.
            mask = np.zeros_like(raw_image)

        # Include some no-good pixels depending on their status
        # as requested by the user.
        # This MUST be done for each mask rather than the combined mask
        # where we only have boolean
        if exclude_from_mask is not None:
            mask = mk.change_mask(mask, exclude_from_mask=exclude_from_mask)

        # Add invalid values to the mask
        to_be_combined = [mask, ~(np.isfinite(raw_image))]

        # Find negative and non masked pixels if any
        negative_values = (raw_image < 0) & (mask == 0)
        nb_negative = np.count_nonzero(negative_values)
        if flag_negative and nb_negative>0:
            LOG.warning(f"{file}: {nb_negative} pixels had negative fluxes and were masked.")
            to_be_combined.append(negative_values)

        mask = mk.combine_masks(to_be_combined)

        exp_time = utils.get_exp_time(metadata)

        # We shift the time by half the duration of the exposure.
        # We do that in the loop to be compatible if all images don't have the same exposure time
        start_time = exp_time + metadata["EFFEXPTM"] / 2

        # EFFINTTM is the Effective Integration Time in (s)
        times.append(start_time)

        images.append(raw_image)
        masks.append(mask)
        metadatas.append(metadata)

    # We create the combined 2D masked array
    global_2d_mask = mk.combine_masks(masks)

    tmp_images = np.stack(images)
    global_mask = np.broadcast_to(global_2d_mask, tmp_images.shape)

    exp_images = np.ma.masked_array(tmp_images, mask=global_mask, fill_value=np.nan)

    times = np.asarray(times)

    # For each exposure, the time will be the center of the exposure.
    # The 0 is the beginning of the first exposure
    times = times - times[0]

    # Get rid of unecessary dimension and list in the case of only one value
    exp_images = np.squeeze(exp_images)
    if len(metadatas) == 1:
        metadatas = metadatas[0]

    return times, exp_images, metadatas


def MIRI_rateints(filenames, exclude_from_mask=None, flag_negative=True):
    """
    Read fits files (rateints) containing all integrations for each dither point
    then return a cube image (one image for each integration, ordered in time)

    Invalid and negative fluxes are masked (with a warning)

    All mask are combined to make sure if one pixels is selected that it's visible for all slices

    :param filenames: List of filenames
    :param exclude_from_mask: In case you want to include pixel types that are normally excluded.
                            Specify the list of pixel status you want to include, as a list
                            - 1    : dead pixel
                            - 2    : hot pixel
                            - 4    : noisy pixel
                            - 8    : high saturation
                            - 16   : pixel saturation mask
                            - 32   : cosmic ray
                            - 64   : noise spike downward
                            - 128  : a noise spike upward
                            - 256  : Looks like a negative cosmic ray (the frames after the high are offset downward).
                            - 512  : No electronic non-linearity correction exists (or has high errors)
                            - 1024 : Ramp contains data outside of electronic linearity correction range.
                            - 2048 : No mean dark correction exists for pixel.
    :param bool flag_negative: [default=True] You can decide you want to include pixels with negative flux (for DARKs for instance)

    :return: time array for middle of integration, Cube (nb_ints*nb_files, y, x), metadata list for every images
    """
    LOG.info("Reading MIRI rateints")

    if isinstance(filenames, str):
        filenames = [filenames]

    # Get header
    with fits.open(filenames[0]) as hdulist:
        (dummy, y_pixels, x_pixels) = hdulist["SCI"].data.shape

    # Don't assume all files have the same number of integrations
    nb_ints = 0
    for file in filenames:
        with fits.open(file) as hdulist:
            nb_ints += hdulist[0].header["NINTS"]

    # Successive images for each integration, with reference image substracted (before bright target slew)
    int_raw_images = np.empty((nb_ints, y_pixels, x_pixels))
    time_int = np.empty(nb_ints)

    masks = []
    metadatas = []
    i2 = 0
    for (id_exp, file) in enumerate(filenames):
        LOG.debug(f"Reading file {file}")
        hdulist = fits.open(file, memmap=False)

        metadata = hdulist[0].header
        n_int = metadata["NINTS"]

        # Create a masked array
        mask = hdulist['DQ'].data

        # Include some no-good pixels depending on their status
        # as requested by the user.
        # This MUST be done for each mask rather than the combined mask
        # where we only have boolean
        if exclude_from_mask is not None:
            mask = mk.change_mask(mask, exclude_from_mask=exclude_from_mask)

        raw_image = hdulist['SCI'].data  # DN/s

        if raw_image.ndim != 3:
            raise ValueError(f"{file} doesn't seem to be MIRI level 2 image-ints data. data shape should have "
                             f"3 dimensions, got {raw_image.ndim} ({raw_image.shape}).")

        # Add invalid values to the mask
        to_be_combined = [mask, ~(np.isfinite(raw_image))]

        # Find negative and non masked pixels if any
        negative_values = (raw_image < 0) & (mask == 0)
        nb_negative = np.count_nonzero(negative_values)
        if flag_negative and nb_negative > 0:
            LOG.warning(f"{file}: {nb_negative} pixels had negative fluxes and were masked.")
            to_be_combined.append(negative_values)

        mask = mk.combine_masks(to_be_combined)

        # Start of the exposure
        start_time = utils.get_exp_time(metadata)

        i1 = i2
        i2 = i1 + n_int

        # Middle of each integration of that exposure
        # EFFINTTM is the Effective Integration Time in (s)
        time_int[i1:i2] = start_time + (np.arange(n_int) + 0.5) * (metadata["EFFINTTM"] + metadata["NRESETS"] *
                                                                   metadata["TFRAME"])
        int_raw_images[i1:i2, :, :] = raw_image

        masks.extend(list(mask))  # We want one mask for each integration, not a big mask for all int of that exp
        metadatas.extend([metadata] * n_int)  # We duplicate the metadata for each int

    # We create the combined 2D masked array
    global_2d_mask = mk.combine_masks(masks)

    global_mask = np.broadcast_to(global_2d_mask, int_raw_images.shape)

    int_images = np.ma.masked_array(int_raw_images, mask=global_mask, fill_value=np.nan)

    # For each exposure, the time will be the center of the exposure.
    # The 0 is the beginning of the first exposure
    time_int = time_int - time_int[0]

    return time_int, int_images.copy(), metadatas


def MIRI_ramps(filenames):
    """
    Read RAW MIRI file and return list of images/metadata corresponding to each file
    Each file must have only one image per exposures (use MIRI_rateints otherwise)

    :param str filenames: List of filenames (or one filename)
    :return: array of middle time for each exposure, Cube image (nb_exp, y, x), metadata for each exposure as a dict
    :rtype: list(np.array(nint, ngroups, ny, nx))
    """
    LOG.info("Reading MIRI ramps")

    if isinstance(filenames, str):
        filenames = [filenames]

    images = []
    metadatas = []
    for file in filenames:
        LOG.debug(f"Reading file {file}")
        hdulist = fits.open(file)

        metadata = hdulist[0].header
        raw_image = hdulist['SCI'].data  # DN

        if raw_image.ndim != 4:
            raise ValueError(f"{file} doesn't seem to be MIRI Ramp data. data shape should have 4 dimensions, "
                             f"only got {raw_image.ndim} ({raw_image.shape}).")

        # Mask doesn't exist for raw data by definition. that's why I don't try to use it here.
        images.append(raw_image)
        metadatas.append(metadata)

    if len(metadatas) == 1:
        metadatas = metadatas[0]
        images = images[0]

    return images, metadatas


def MIRI_mask_statistics(filename, min_pix=3):
    """
    Read a MIRI file, retrieve the mask and get statistics out of it.

    :param str filename: filename of the MIRI file
    :param int min_pix: [optional] (Default 3), minimum number of pixel with a given status to be displayed
    """

    with fits.open(filename) as hdulist:
        mask = hdulist['DQ'].data

    print(mk.mask_statistic(mask, min_pix=min_pix))


def compare_headers(filenames, exclude_keywords=None):
    """
    Take a list of FITS filenames and return an analysis of the first headers.

    Part I: Common values
    Display the key / values that are identical for all the files

    Part II: Values that differ
    Display as a nice table the list of keys and the corresponding values for each files

    :param list(str) filenames:
    :param list(str) exclude_keywords: [Optional] List of keywords to hide in Part II (nothing is hidden in part I).
                                       By default, this is the list of keywords hidden:
                                       ['BENDTIME', 'BMIDTIME', 'BSTRTIME', 'DATE', 'DATE-BEG', 'DATE-END', 'EPH_TIME',
                                       'EXPEND', 'EXPMID', 'EXPSTART', 'FILENAME', 'HENDTIME', 'HMIDTIME', 'HSTRTIME',
                                       'OSF_FILE', 'TIME-OBS']
    :return:
    """

    string_report = ""

    if exclude_keywords is None:
        exclude_keywords = ['BENDTIME', 'BMIDTIME', 'BSTRTIME', 'DATE', 'DATE-OBS', 'DATE-BEG', 'DATE-END', 'EPH_TIME',
                            'EXPEND', 'EXPMID', 'EXPSTART', 'FILENAME', 'HENDTIME', 'HMIDTIME', 'HSTRTIME', 'OSF_FILE',
                            'TIME-OBS']

    headers = []

    all_keys = []  # Prepare the list of all keys for all fits files (need to use set() before using this variable after the loop)
    for file in filenames:
        hdulist = fits.open(file)
        header = hdulist[0].header

        all_keys.extend(header.keys())

        headers.append(header)
        hdulist.close()
    all_keys = set(all_keys)

    # Find the list of keys whose values don't change from one file to the other
    header_sets = [set(d.items()) for d in headers]

    common_set = header_sets[0] & header_sets[1]
    for s in header_sets[2:]:
        common_set = common_set & s

    common_keys = list(set([k for k, v in common_set]))
    common_keys.sort()

    # Delete empty string that correspond to section title in FITS header
    try:
        common_keys.remove("")
    except ValueError:
        pass

    changing_keys = list(all_keys - set(common_keys) - set(exclude_keywords))
    changing_keys.sort()

    # Delete empty string that correspond to section title in FITS header
    try:
        changing_keys.remove("")
    except ValueError:
        pass

    string_report += "Common values:\n"
    header = headers[0]  # Just choose one, values are all the same anyway
    for k in common_keys:

        string_report += f"\t{k}: {header[k]}\n"

    string_report += "\nUnique values:\n"

    values = []
    for file, header in zip(filenames, headers):
        tmp = [file]
        for k in changing_keys:
            try:
                value = header[k]
            except KeyError:
                # N/A if key don't exist
                value = "N/A"

            tmp.append(value)
        values.append(tmp)


    columns = ["Filename"]
    columns.extend(changing_keys)


    string_report += tabulate.tabulate(values, headers=columns)

    return string_report
