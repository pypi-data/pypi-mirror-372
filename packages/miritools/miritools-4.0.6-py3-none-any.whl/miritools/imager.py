"""
Image related functions
"""

from typing import Tuple, Dict, Optional, List

import matplotlib.patches as patches
import numpy as np
from photutils.aperture import CircularAperture
from photutils.aperture import aperture_photometry
from photutils.aperture import CircularAnnulus
from scipy import ndimage

import logging

from . import imlib
from . import mask as mk

LOG = logging.getLogger(__name__)

color_list = ["#ff0000", "#0000ff", "#000000", "#3cb44b", "#ffe119", "#0082c8", "#911eb4",
                  "#46f0f0", "#f032e6", "#d2f53c", "#fabebe", "#008080", "#e6beff",
                  "#aa6e28", "#fffac8", "#800000", "#aaffc3", "#808000", "#ffd8b1",
                  "#000080", "#808080", "#FFFFFF"]


def analyse_aperphot(integration_images, x, y, radius, inner_radius, outer_radius, label_id=1):
    """
    Given the center coordinate and size of aperture photometry, return the time evolution of the aperture photometry
    flux and a patches.Circle object the position of the aperture photometry

    Note that the func used should deal with NaNs that are highly probable in an astronomical image.

    :param integration_images: input cube (nb_integrations, y, x)
    :param float radius: size for the flux circle to consider (in pixels)
    :param float inner_radius: inner radius (in pixels) used for the annulus evaluating the background level
    :param float outer_radius: outer radius (in pixels) used for the annulus evaluating the background level
    :param int x: x pixel coordinate for the box center
    :param int y: y pixel coordinate for the box center
    :param int label_id: [optional] In case of multiple boxes, allow to number them

    :return: tuple of patches (1 circle + 1 annulus) that represent the aperture and "mean" flux over time
    :rtype: tuple(patches), nd.array(nb_integrations)
    """

    # Set counter
    if label_id is None:
        label_id = 1

    color_aper = color_list[label_id - 1]

    aper = CircularAperture((x, y), r=radius)
    annulus_aper = CircularAnnulus((x, y), r_in=inner_radius, r_out=outer_radius)

    apers = [aper, annulus_aper]

    a = np.ndim(integration_images)

    if a == 3:
        nz, ny, nx = integration_images.shape
    elif a == 2:
        ny, nx = integration_images.shape

    if a == 3:
        flux = np.zeros(nz)
        for i in np.arange(nz):
            phot_table = aperture_photometry(integration_images[i, :, :], apers)

            bkg_mean = phot_table['aperture_sum_1'] / annulus_aper.area
            object_mean = phot_table['aperture_sum_0'] / aper.area
            flux_per_pixel = object_mean - bkg_mean

            flux[i] = flux_per_pixel
    elif a == 2:
        phot_table = aperture_photometry(integration_images, apers)

        bkg_mean = phot_table['aperture_sum_1'] / annulus_aper.area
        object_mean = phot_table['aperture_sum_0'] / aper.area
        flux_per_pixel = object_mean - bkg_mean

        flux = flux_per_pixel

    aperture = patches.Circle((x, y), radius, edgecolor=color_aper, fill=False,
                              label="Aperture {} (width={})".format(label_id, radius))

    aperture_inner = patches.Circle((x, y), inner_radius, edgecolor=color_aper, fill=False)

    aperture_outer = patches.Circle((x, y), outer_radius, edgecolor=color_aper, fill=False)

    output_patches = (aperture, aperture_inner, aperture_outer)

    return output_patches, flux


def analyse_box(integration_image, x, y, box_dims, func=np.nanmean, label_id=None):
    """
    Given the center coordinate and size of a box, return the time evolution of the "mean"
    (default, see 'func' parameter) flux of that box and a patches.Rectangle object that
    match the designed box

    Note that the func used should deal with NaNs that are highly probable in an astronomical image.

    :param integration_image: input cube (nb_integrations, y, x)
    :param box_dims: dimensions of box (if int given, it's a square, if a tuple, (width, height)
    :type box_dims: int or tuple(int, int)
    :param int x: x pixel coordinate for the box center
    :param int y: y pixel coordinate for the box center
    :param Callable[[float], float] func: Numpy function to use across the box (np.nanmean, np.nanmax, np.nanmin,
                 np.nanmedian, np.nanstd or other). If None, will return the sub-image or sub-cube instead.
    :param int label_id: [optional] In case of multiple boxes, allow to number them

    :return: Tuple of patche (1 rect here) that represent the box and "mean" (default, see 'func' parameter) flux over time
    :rtype: tuple(patches), nd.array(nb_integrations) (or nd.array(time, x_box, y_box) if func=None)
    """

    if isinstance(box_dims, int):
        box_dims = (box_dims, box_dims)

    # Set counter
    if label_id is None:
        label_id = 1

    color_box = color_list[label_id - 1]

    flux = simplified_analyse_box(integration_image, box_dims, x, y, func)

    box = patches.Rectangle((x - (box_dims[0] / 2), y - (box_dims[1] / 2)), box_dims[0], box_dims[1],
                            edgecolor=color_box, fill=False,
                            label="Box {} (size={})".format(label_id, box_dims))

    output_patches = (box,)

    return output_patches, flux


def analyse_mask(integration_image, selection, func=np.nanmean):
    """
    Given a selection mask of pixel we want to keep, return the time evolution of the "mean"
    (default, see 'func' parameter) flux of that selection and the final_mask (corresponding to ALL pixels MASKED, 
    meaning that if a pixel is not masked in this output, it is analysed)

    Note that the func used should deal with NaNs that are highly probable in an astronomical image.

    :param integration_image: input cube (time, y, x)
    :param selection: Mask to apply to each individual image to select the pixels (a value of 1 mean the pixel is selected,
                 a zero value mean he's masked)
    :type selection: ndarray(y, x)
    :param Callable[[float], float] func: Numpy function to use across the box (np.nanmean, np.nanmax, np.nanmin,
                 np.nanmedian, np.nanstd or other)

    :return: mask array (0: not masked, >0: masked) as in ma.masked_array &
             flux (depending on the function used) over time
    :rtype: nd.array(y, x), nd.array(nb_integrations)
    """

    # Combine the mask with the already existing mask in the input data if necessary
    if isinstance(integration_image, np.ma.masked_array):
        # Each of the input slice should have the same mask
        mask = mk.combine_masks([~selection, integration_image.mask[0]])
    else:
        mask = ~selection

    global_mask = np.broadcast_to(mask, integration_image.shape)

    int_images = np.ma.masked_array(integration_image, mask=global_mask, fill_value=np.nan)

    flux = func(int_images, axis=(1, 2))

    return mask, flux


def simplified_analyse_box(integration_image, box_dims, x, y, func=np.nanmean):
    """
    Given the center coordinate and size of a box, return the time evolution of the "mean"
    (default, see 'func' parameter) flux of that box and a patches.Rectangle object that
    match the designed box

    Note that the func used should deal with NaNs that are highly probable in an astronomical image.

    The global name "reference_filename" must exist, to display it in the plot

    :param integration_image: input cube (time, y, x)
    :param box_dims: dimensions of box (if int given, it's a square, if a tuple, (width, height)
    :type box_dims: int or tuple(int, int)
    :param int x: x pixel coordinate for the box center
    :param int y: y pixel coordinate for the box center
    :param Callable[[float], float] func: Numpy function to use across the box (np.nanmean, np.nanmax, np.nanmin,
                 np.nanmedian, np.nanstd or other). If None, will return the sub-image or sub-cube instead.

    :return: "mean" (default, see 'func' parameter) flux over time
    :rtype: nd.array(time) (or nd.array(time, x_box, y_box) if func=None)
    """

    nt, ny, nx = integration_image.shape

    if isinstance(box_dims, int):
        box_dims = (box_dims, box_dims)

    half_width = int(box_dims[0] / 2)
    half_height = int(box_dims[1] / 2)

    # Boundaries check in addition to index calculation
    x_begin = max(x - half_width, 0)
    x_end = min(x + half_width, nx)
    y_begin = max(y - half_height, 0)
    y_end = min(y + half_height, ny)

    sub_image = integration_image[:, y_begin:y_end, x_begin:x_end]

    if func is None:
        return sub_image
    else:
        return func(sub_image, axis=(1, 2))


def get_pixel_coordinates(reference_image: np.ndarray, ref_metadata: Dict, nb_pixels: int, fmin: float = 0.01,
                          fmax: float = 0.9) -> Tuple[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]:
    """
    Will sort pixels by brightness and retrieve 'nb_pixels' from it,
    sampling the dynamic flux range

    NOTE: searchsorted and digitize don't work with masked array because they ignore the mask. The fact that my
    array is 2D is also a problem for some methods since I want the indexes.
    2D array and mask is an explosive combination

    Masked pixels are sorted at the end of the array and avoided.
    Pixels lower than 0 are avoided as well
    From the remaining pixels, the selected one will be between 10% and 90% of
    the remaining range (in term of pixel, not brightness), leaving the 10% faintest and 10% brightest out.

    :param reference_image: Reference 2D image.
    :type reference_image: np.array(ny, nx)
    :param dict ref_metadata: metadatas associated with the reference image
    :param int nb_pixels: Number of pixels you want
    :param float fmin: [optional] flux min for sampling. 0.1 will mean "min_flux + 10% * (max_flux - min_flux)"
    :param float fmax: [optional] flux max for sampling. 0.9 will mean "90% * max_flux"
    :return: ref pixels and absolute pixel (in full array) coordinates in a tuple. Each tuple is (y_array, x_array).
             Tuple of Y-index then X-index arrays, each array having one
             value per pixel. The format is compatible with numpy, meaning you can do my_array[y_array, x_array] and
             get the selected values
    :rtype:
    """

    # Copy input to ensure we don't change the underlying mask in this function
    ref = reference_image.copy()

    # ref.min/max sometimes doesn't work and return nan
    im_max = np.nanmax(ref)
    im_min = max(np.nanmin(ref), 0)

    min_flux = im_min + (im_max - im_min) * fmin
    max_flux = im_max * fmax

    flux_sampling = np.linspace(min_flux, max_flux, nb_pixels)

    ref_pixels = []
    for flux in flux_sampling:
        diff = np.abs(ref.data - flux)
        argmin = np.nanargmin(diff)  # Ignore Nan (masked values are set to NaN)
        pix = np.unravel_index(argmin, ref.shape)

        # Mask the selected pixel to ensure we don't use it for another flux bin
        ref.mask[pix] = True
        ref_pixels.append(pix)

    if len(set(ref_pixels)) != nb_pixels:
        raise ValueError("The same pixel was used at least twice because of insufficient flux sampling")

    ref_pixels = np.asarray(ref_pixels)

    # Get absolute pixel coordinates. For a full array reference image, ref_pixels and abs_pixels will be identical
    x_start = ref_metadata["SUBSTRT1"] - 1  # Because FITS start at 1, but indexes in Python start at 0
    y_start = ref_metadata["SUBSTRT2"] - 1  # Because FITS start at 1, but indexes in Python start at 0
    abs_pixels = ref_pixels.copy()
    abs_pixels[:, 0] += y_start
    abs_pixels[:, 1] += x_start

    return tuple(ref_pixels.T), tuple(abs_pixels.T)


def crop_image(big_image: np.ndarray, small_image: np.ndarray, big_meta: Optional[Dict] = None,
               small_meta: Optional[Dict] = None) -> np.ndarray:
    """
    Will crop the first image to the size of the second image. If metadatas are provided for both images, with shift the
    first image to the position of the second, using SUBSTRT1 and SUBSTRT2 metadata

    :param big_image: Image to be cropped
    :param small_image:
    :param big_meta:   [Optional] Metadata dict for big image
    :param small_meta: [Optional] Metadata dict for small image
    :return: Cropped image of big image (same shape as small image)
    :rtype: np.array(y, x)
    """

    (y_size, x_size) = small_image.shape

    if (big_meta is None) != (small_meta is None):
        raise ValueError("One header is defined but the other is missing.")

    if big_meta is None or small_meta is None:
        y_start = 0
        x_start = 0
    else:
        x_big = big_meta["SUBSTRT1"] - 1  # Because FITS start at 1, but indexes in Python start at 0
        y_big = big_meta["SUBSTRT2"] - 1  # Because FITS start at 1, but indexes in Python start at 0

        x_small = small_meta["SUBSTRT1"] - 1  # Because FITS start at 1, but indexes in Python start at 0
        y_small = small_meta["SUBSTRT2"] - 1  # Because FITS start at 1, but indexes in Python start at 0

        y_start = y_small - y_big
        x_start = x_small - x_big

    y_stop = y_start + y_size
    x_stop = x_start + x_size

    # We don't want to change the original image via cropped
    cropped_image = big_image[y_start:y_stop, x_start:x_stop].copy()

    return cropped_image


def abs_to_rel_pixels(abs_coords: Tuple[int, int], metadatas: Dict) -> Tuple[int, int]:
    """
    Given absolute coordinates (Coordinates in fictious FULL array), will return the coordinates for the current image
    (as described by metadatas) given its point of origin and size.

    Will return an IndexError if the calculated index is outside the range of the image.

    :param abs_coords: Absolute coordinates (x, y)
    :param metadatas:
    :return: Relative coordinates depending on the Sub-array if there's one (x, y)
    """

    (abs_x, abs_y) = abs_coords

    rel_x = abs_x - (metadatas["SUBSTRT1"] - 1)
    rel_y = abs_y - (metadatas["SUBSTRT2"] - 1)

    x_max = metadatas["SUBSIZE1"] - 1
    y_max = metadatas["SUBSIZE2"] - 1
    if (rel_x < 0) or (rel_y < 0) or (rel_x > x_max) or (rel_y > y_max):
        LOG.exception(
            "Pixel coordinates (x,y)=({},{}) outside of Image range (Xmax,Ymax)=({},{})".format(rel_x, rel_y, x_max,
                                                                                                y_max))
        raise IndexError

    return rel_x, rel_y


def find_array_intersect(metadatas: List[Dict]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """
    Given a list of metadatas dictionaries, will return the absolute coordinates that are common to all images

    :param metadatas: list of metadata dictionaries, one per image

    :return: Coordinates of [(x_min, x_max), (y_min, y_max)] that define the common rectangle of all images. Return None
             if no common indexes exists bot X, Y or both
             Note: You define the rectangle with [x_min:x_max+1, y_min:y_max+1] meaning the maximum pixel index
             is (x_max, y_max)
    """

    x_starts = []
    x_stops = []
    y_starts = []
    y_stops = []

    for meta in metadatas:
        x_start = meta["SUBSTRT1"] - 1
        y_start = meta["SUBSTRT2"] - 1
        x_stop = x_start + meta["SUBSIZE1"]
        y_stop = y_start + meta["SUBSIZE2"]

        x_starts.append(x_start)
        x_stops.append(x_stop)
        y_starts.append(y_start)
        y_stops.append(y_stop)

    x_min = np.max(x_starts)
    y_min = np.max(y_starts)
    x_max = np.min(x_stops)
    y_max = np.min(y_stops)

    if x_min > x_max:
        x_range = None
    else:
        x_range = (x_min, x_max)

    if y_min > y_max:
        y_range = None
    else:
        y_range = (y_min, y_max)

    return x_range, y_range


def select_sub_image(image, center, radius, corner=False):
    """
    Select a subarray from an input image, given a center and a radius (here equivalent to a half-width of a square)

    :param image: input 2D image
    :type image: np.array(y, x)
    :param center: Center (y,x) (in pixels). Float will be force converted to int
    :type center: tuple(int, int)
    :param int radius: half-width of the cropped image (width = 2 * size + 1). Float will be force converted to int
    :param bool corner: By default, False. Return the corner coordinates (y,x) as 2nd value of a tuple with image.
    :return: cropped image with size = 2 * radius + 1 for each dimension. If corner=true, return the coordinates (y,x)
             of the lower left corner
    :rtype: np.array(y, x)
    """

    yc, xc = center

    # Force conversion to integer
    xc = int(xc)
    yc = int(yc)
    radius = int(radius)

    x1 = xc - radius
    x2 = xc + radius
    y1 = yc - radius
    y2 = yc + radius

    x1min = y1min = 0
    (y2max, x2max) = image.shape

    # Index go from 0 to shape - 1
    if (x1 < x1min) or (x2 >= x2max) or (y1 < y1min) or (y2 >= y2max):
        raise ValueError(f"sub-image (center: {center} ; half-size: {radius}) cross border of array of shape {image.shape}")

    sub_image = image[y1:y2+1, x1:x2+1]

    if corner:
        return sub_image, (y1, x1)
    else:
        return sub_image


def subpixel_shift(image, dy, dx):
    """
    Shift an image with a sub-pixel precision.
    This uses a property of the Fourier transform :
    a shift in the space domain corresponds to a phase rotation in the frequency domain.
    For integer shift, this method gives the same result that numpy roll function, within numerical precision
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.fourier_shift.html

    :param image: The input image. By default, we expect a 2D image. If a cube is given, we assume (n_slices, ny,
    nx) and apply the shifts to the first 2 dimensions.
    :type image: np.ndarray(ny, nx), float
    :param float dy: shift on the y axis
    :param float dx: shift on the x axis

    :return: shifted image
    :rtype: np.ndarray(ny, nx), float
    """
    shifts = [dy, dx]
    if image.ndim > 2:
        for i in range(image.ndim - 2):
            shifts.insert(0, 0)
    
    intermediate = ndimage.fourier_shift(np.fft.fftn(image), shifts)
    result = np.fft.ifftn(intermediate).real
    return result


def radial_profiles(data, center=None, bin_width=1, rmax=None, edges=None, funcs=None):
    """
    original source: https://people.ucsc.edu/~ianc/python/_modules/radial_data.html#radial_data
    r = radial_statistics(data,annulus_width,working_mask,x,y)

    A function to reduce an data to a radial cross-section. Each annulus contains values inside the range
    [r; r+bin_width[ except for the last bin where values are from [r; r+bin_width]

    parameters
    ---------
    :param data: whatever data you are radially averaging.  Data is
        binned into a series of annuli of width 'bin_width'
        pixels. A mask can be provided if data is a MaskedArray

    :type data: np.array or np.ma.MaskedArray

    :param bin_width: float
        [optional] width of each annulus.  Default is 1.

    :param center: (float, float)
        [optional] floating index tuple for the center (y, x) of the radial distribution.
        If not given, will be the center of the array

    :param rmax: int
        [optional] maximum radial value over which to compute statistics. By default, max radius available to us

    :param edges: nd.array
        [optional] list of n+1 edges for the n bins. If set, bin_width and rmax are ignored

    :param funcs: list(callable)
        [optional] provide the list of functions you want to apply to each annulus (e.g. mean or np.nanmean)
        By default, a prefined set of functions is applied
    output
    -----
    :return r: contain the following statistics, computed across each annulus
        key:
        "r"        - the radial coordinate used (center of annulus)
        "mean"     - mean of the data in the annulus
        "sum"      - the sum of all enclosed values at the given radius
        "std"      - standard deviation of the data in the annulus
        "median"   - median value in the annulus
        "variance" - variance value in the annulus
        "max"      - maximum value in the annulus
        "size"     - number of elements in the annulus
        NOTE: that the list of keys will change if you specify your custom list of callable to apply to the data bins
             Only 'r' will remain
    :rtype: dict
    """

    # ---------------------
    # Set up input parameters
    # ---------------------
    # If data is already a Masked array, we just overwrite the fill_value, the mask is kept
    data = np.ma.MaskedArray(data, fill_value=np.nan)
    mask = data.mask

    npiy, npix = data.shape

    # Create mesh
    if center is None:
        center = (npiy / 2., npix / 2.)

    x1 = np.arange(0, npix)
    y1 = np.arange(0, npiy)

    x, y = np.meshgrid(x1, y1)

    r = abs(x - center[1] + 1j * (y - center[0]))

    if rmax is None:
        rmax = r[~mask].max()

    radialdata = imlib._binned_statistic(r, data, bin_width=bin_width, xrange=(0, rmax), edges=edges, funcs=funcs)

    return radialdata


def radial_profile(data, func=np.nanmean, **kwargs):
    """
    Compute radial profile of a given data, provided a center and a function (nanmean is used as a default)

    Other parameters unknown to this function will be passed to radial_profiles (which is called internally).
    See radial_profiles documentation for more info on the parameters available

    :param data: input 2D image (floats)
    :type data: np.array(y, x)
    :param callable func: [optional] By default, np.nanmean, but can be any callable to apply to all annulus

    :return: radius (pixels) and mean profile (data unit)
    :rtype: tuple(np.array(float), np.array(float))
    """
    if not callable(func):
        raise ValueError(f"func is not callable: {func.__name__}")

    profile = radial_profiles(data=data, funcs=[func], **kwargs)

    return profile["r"], profile[func.__name__]
