"""
Mask related functions
"""
import os
from astropy.io import fits
import numpy as np
import logging

from . import constants

LOG = logging.getLogger(__name__)


def change_mask(mask, exclude_from_mask):
    """
    Change mask intended for a MaskedArray before actually creating the array. A real mask is boolean, but in a
    MIRI .fits file, you have integers that have a complex structure.
    Each value is a combination of several status that you might want

    You can substract a combined status, like 928 for instance (32, 128, 256, 512)
    and that will only affect pixels that have this specific value.

    Or you can give a specific status (a power of 2). If given that status, we will affect all concerned pixels,
    whether they possess only that status or not.

    :param mask: ND array containing values. By default, 0 is correct and all others are not
    :type mask: np.array(y, x)
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
    :type exclude_from_mask: list(int)

    :return: modified mask
    :rtype: np.ndarray
    """

    if not isinstance(exclude_from_mask, (list, tuple, np.array)):
        raise ValueError(f"exclude_from_mask must be a list of integers (you provided '{exclude_from_mask}')")

    out_mask = mask.astype(int)
    for val in exclude_from_mask:
        # Status can be combined and added. We just want to remove one specific status for all pixels

        # If value is a power of 2, it's a unique status we want to
        # substract to all concerned pixels (that might contain other status)
        if ((val & (val - 1)) == 0) and val > 0:
            # Identify pixels that contain this specific status
            status_pixel = np.bitwise_and(out_mask, val)
            out_mask -= status_pixel  # Substract this status to all concerned pixels (all other have 0)
        else:
            out_mask[out_mask == val] = 0

    return out_mask


def combine_masks(masks):
    """
    Combine a list of masks into one array. We use what np.MaskedArray uses.
    If 0, we keep the data, if not we mask it

    :param masks: List of masks, all having the same shape. Values can be integers
    :type masks: list(np.array)

    :return: One combined masks where we keep data only if visible throughout all the masks. Output mask will be boolean
    :rtype: np.array
    """

    combined_mask = masks[0].copy()  # By default we keep everything

    # If a pixel was previously masked, or is masked by the current image, we mask
    for mask_tmp in masks[1:]:
        combined_mask = np.logical_or(combined_mask, mask_tmp)

    return combined_mask


def decompose_mask_status(x):
    """
    Given a mask value, decompose what sub-status compose it

    Example:
    One pixel mask value is 928:

    928 decompose into 32, 128, 256, 512

    :param int x: DQ value that need to be decomposed into individual flag values

    :return: list of all DQ flags that compose the input value
    """
    powers = []
    i = 1
    while i <= x:
        if i & x:
            powers.append(i)
        i <<= 1
    return powers


def decompose_to_bits(x):
    """
    Decompose decimal number into individual bits as a list

    i.e
    >>> decompose_to_bits(32)
    [5]
    >>> decompose_to_bits(31)
    [0,1,2,3,4]

    :param x:
    :return:
    """

    bin_str = bin(x)[2:]
    nb_bits = len(bin_str)

    bits = []
    for i in reversed(range(nb_bits)):
        # If that bit is included, add it's number (reverse from its position)
        if bin_str[i] == "1":
            bits.append(nb_bits - i - 1)

    return bits


def mask_statistic(mask, min_pix=3, status=None):
    """
    Return a string that detail mask statistics.

    List of DQ statuses for the pipeline are given here:
    https://jwst-pipeline.readthedocs.io/en/latest/jwst/references_general/references_general.html#data-quality-flags

    Example:
    >>> print(mask_statistic(mask))
    Pixel status 0: Good pixel
        941694 pixels
    Pixel status 1: Dead pixel
        5525 pixels
    Pixel status 2: Hot pixel
        8024 pixels
    Pixel status 32: Cosmic ray
        101525 pixels

    :param mask: Input 2D image with integer values for masked array
    :param min_pix: [Optional] If given, filter pixels status that affect less or equal than that amount of
                    pixels. (default: 3)
    :param str status: [optional] By default, status given by DQ of pipeline.
                       But you can ask for statuses given by DHAS with "DHAS"

    :return: Report on mast statistic as string (see exemple above)
    """

    if status == "DHAS":
        status_comment = constants.status_dhas
    else:
        status_comment = constants.status_pipeline

    # Fill dict with unknown statuses
    val = np.max(list(status_comment.keys()))
    while val < 2**32:
        val <<= 1  # val = val*2
        status_comment[val] = "Unknown pixel status"

    unique, counts = np.unique(mask, return_counts=True)

    # Sort items in reverse order
    sorted_cnts = np.argsort(counts)
    unique = unique[sorted_cnts[::-1]]
    counts = counts[sorted_cnts[::-1]]

    msg = ""
    for (status_val, count) in zip(unique, counts):
        if count <= min_pix:
            continue

        try:
            status_dissected = "    {}\n".format(status_comment[status_val])
        except KeyError:
            # If not a power of 2, this is a composed status of several pixel individual statuses
            sub_status = decompose_mask_status(int(status_val))

            status_dissected = ""
            for s in sub_status:
                status_dissected += "    {}: {}\n".format(s, status_comment[s])

        msg += "Pixel status {}: {} pixels\n".format(int(status_val), count)
        msg += "{}\n".format(status_dissected)

    return msg


def get_separated_dq_array(dq_mask):
    """
    Will split the DQ mask array into individual status for each pixels.
    Image (y,x) will then become a cube (y, x, 32)

    Copy paste of the answer here: https://stackoverflow.com/a/51509307/1510480

    output[:,:,0] represent the 0-th order flag (2^0=1)
    output[:,:,1] represent the 1-th order flag (2^1=2)
    ... and so on

    :param dq_mask: Input 2D array of int-type values representing JWST DQ flags
    :type dq_mask: np.array(y, x)

    :return: Data cube np.array(y, x, 32), one slice for each power of 2
    """
    num_bits = 32
    if np.issubdtype(dq_mask.dtype, np.floating):
        raise ValueError("numpy data type needs to be int-like")
    xshape = list(dq_mask.shape)
    dq_mask = dq_mask.reshape([-1, 1])
    mask = 2**np.arange(num_bits, dtype=dq_mask.dtype).reshape([1, num_bits])

    return (dq_mask & mask).astype(bool).reshape(xshape + [num_bits])


def simple_stats(dq_mask, statuses=None):
    """

    :param dq_mask: 2D mask
    :param dict statuses: key: bit (i.e. 1 mean 2**1) ; value: flag description
    :return:
    """
    indiv_mask = get_separated_dq_array(dq_mask)

    # Good pixels are treated separately
    nb_pixels = np.count_nonzero(dq_mask == 0)
    output = f"0: {nb_pixels} (Good pixels)\n"
    
    if statuses is None:
        statuses = constants.status_pipeline

    for idx in range(32):
        value = 2**idx  # trick to also have 0 for idx=-1, because theses are good pixels, so without a flag in
        # practice
        comment = statuses[idx]
        nb_pixels = np.count_nonzero(indiv_mask[:,:,idx])

        output += f"{2**idx}: {nb_pixels} ({comment})\n"

    return output


def extract_flag_image(mask, flag):
    """
    From the DQ mask image, extract the image corresponding to the input flag. This flag can also be a combination
    of individual flags.

    :param mask: DQ image
    :param int flag: flag value
    :return: flag image. 1 if the pixel is flagged, 0 if not
    """

    if not isinstance(flag, int):
        raise ValueError(f"flag ({flag}) must be an int.")

    full_mask = get_separated_dq_array(mask)
    full_mask = full_mask.astype("uint8")

    bits = decompose_to_bits(flag)

    flag_image = np.ones_like(mask, dtype="uint8")

    # prepare slice object on unknown number of dimensions, to change only the value of the last dimension
    ind = [slice(None)] * full_mask.ndim

    # Combine all individual flag images in case of a combined flag
    for bit in bits:
        ind[-1] = bit
        flag_image &= full_mask[tuple(ind)]

    return flag_image


def mask_mrs_slices(image, metadatas, cdp_dir, version):
    """
    Given an image or cube image, will add to the mask all pixels not in the slices.
    Currently hardcoded, the threshold to be considered outside the slice is a transmission <80%

    :param image: input image(s)
    :type image: np.ma.MaskedArray(y, x) or np.ma.MaskedArray(nb_images, y, x)
    :param metadatas: header(s)
    :type metadatas: dict or list(dict)
    :param str cdp_dir: folder where DISTORTION CDP are located
    :param str version: cdp version (By default '08.05.00')
    :return:
    """

    if isinstance(metadatas, list):
        multiple = True
        metadata = metadatas[0]
    else:
        multiple = False
        metadata = metadatas

    band = metadata["BAND"]
    channel = metadata["CHANNEL"]
    detector = metadata["DETECTOR"]

    cdp_file = f"MIRI_FM_{detector}_{channel}{band}_DISTORTION_{version}.fits"
    cdp_path = os.path.join(cdp_dir, cdp_file)

    if not os.path.isfile(cdp_path):
        raise ValueError(f"Unable to find Distortion CDP: {cdp_path}.")

    # import parameters needed for d2c mapping
    hdulist = fits.open(cdp_path)

    # Slice idx 0-8: 10%-90%
    slice_idx = 7
    slice_map = hdulist['Slice_Number'].data[slice_idx, :, :]

    # Convert so that a slice is flagged as 0, and all the rest is at 1 (hence masked)
    slice_map = (slice_map == 0).astype(int)

    if multiple:
        # We create the combined 2D masked array
        global_2d_mask = combine_masks((image.mask[0], slice_map))

        global_mask = np.broadcast_to(global_2d_mask, image.shape)

    else:
        global_mask = combine_masks((image.mask, slice_map))

    # Can't update image.mask directly, I have to create a new array to update the mask

    return np.ma.masked_array(image, global_mask)
