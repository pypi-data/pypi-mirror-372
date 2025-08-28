from astropy.io import fits
import numpy as np
import os
from astropy.visualization import interval
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches

import logging

from . import constants
from . import flux
from . import utils
from . import mask as mk

LOG = logging.getLogger(__name__)


def double_image(image1, image2, ititles=None, vlabel=None, title=None, force_positive=False):
    """
    Plot two images using the same Zscale

    :param image1: Input image, Normalisation will be done on that image
    :type image1: np.ndarray(y, x)
    :param image2: Input image
    :type image2: np.ndarray(y, x)
    :param list(str) ititles: [optional] If given, will be one title per image
    :param str vlabel: [optional] Unit of image data
    :param str title: [optional] Image title
    :param bool force_positive: [optional] If True, will force the Zscale vrange to display only positive values

    :return: return the figure
    :rtype: Matplotlib.Figure
    """
    if ititles is not None:
        if not isinstance(ititles, (list, tuple)):
            raise ValueError(f"Expect ititles to be list or tuple of strings, was given '{ititles}'")

        if len(ititles) != 2:
            raise ValueError(f"Expect 2 values (one title per image), got {len(ititles)} instead.")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), sharex=True, sharey=True)  # figsize=(8, 3)
    fig.subplots_adjust(left=0.05, bottom=0.05, right=0.99, top=0.96, wspace=0.1, hspace=0.1)

    zscale = interval.ZScaleInterval(n_samples=600, contrast=0.25, max_reject=0.5, min_npixels=5, krej=2.5,
                                     max_iterations=5)

    if force_positive:
        (vmin, vmax) = zscale.get_limits(image1[image1 > 0])
    else:
        (vmin, vmax) = zscale.get_limits(image1)

    normalization = colors.Normalize(vmin=vmin, vmax=vmax)  # Linear

    cmap = ax1.imshow(image1, origin='lower', norm=normalization, cmap="viridis")
    ax1.set_xlabel("X [pixels]")
    ax1.set_ylabel("Y [pixels]")
    if ititles is not None:
        ax1.set_title(ititles[0])

    cmap = ax2.imshow(image2, origin='lower', norm=normalization, cmap="viridis")
    ax2.set_xlabel("X [pixels]")
    ax2.set_ylabel("Y [pixels]")
    if ititles is not None:
        ax2.set_title(ititles[1])

    cbar = fig.colorbar(cmap, ax=fig.get_axes())
    if vlabel is not None:
        cbar.set_label(vlabel)

    if title is not None:
        fig.suptitle(title)

    return fig

def single_image(image, vlabel=None, title=None, force_positive=False):
    """
    Plot a simple image using Zscale

    :param image: Input image
    :type image: np.ndarray(y, x)
    :param str vlabel: [optional] Unit of image data
    :param str title: [optional] Image title
    :param bool force_positive: [optional] If True, will force the Zscale vrange to display only positive values

    :return: return the figure
    :rtype: Matplotlib.Figure
    """

    fig, ax = plt.subplots()  # figsize=(8, 3)

    zscale = interval.ZScaleInterval(n_samples=600, contrast=0.25, max_reject=0.5, min_npixels=5, krej=2.5,
                                     max_iterations=5)

    if force_positive:
        (vmin, vmax) = zscale.get_limits(image[image > 0])
    else:
        (vmin, vmax) = zscale.get_limits(image)

    normalization = colors.Normalize(vmin=vmin, vmax=vmax)  # Linear

    cmap = ax.imshow(image, origin='lower', norm=normalization, cmap="viridis")

    cbar = fig.colorbar(cmap, ax=ax)
    if vlabel is not None:
        cbar.set_label(vlabel)

    if title is not None:
        fig.suptitle(title)

    ax.set_xlabel("X [pixels]")
    ax.set_ylabel("Y [pixels]")

    return fig


def skycube_spectrum(filename, pix):
    """
    Extract spectrum from input filename for the given pixel and display it

    WARNING: Some unit error can remain, be carefull and test it, I'm not sure, in particular I'm not certain that
    the unit is Jansky and not Jansky/something else

    :param str filename: input skycube FITS file (for MIRI MRS)
    :param pix: pixel coordinates to display (alpha, beta), start at 0. Cube has a size of (alpha, beta) = (19,21).
    :type pix: tuple(int, int)

    :return: wavelengths (microns) and signal (mJy)
    :rtype: tuple(np.array(float), np.array(float))
    """
    alpha, beta = pix

    hdulist = fits.open(filename)

    header = hdulist[0].header
    cdelt1 = abs(header["CDELT1"])
    cdelt2 = abs(header["CDELT2"])

    pixel_area_arcsec = cdelt1 * cdelt2  # arcsec^2

    # field is necessary to have a numpy array instead of a FITS_rec
    wave = hdulist["WAVELENGTH"].data.field("wavelength")
    cube = hdulist[0].data

    dwave = np.zeros_like(wave)
    dwave[:-1] = np.diff(wave)
    dwave[-1] = dwave[-2]  # Because np.diff has n-1 values

    # input Signal is in photon/s/pixel
    signal_1pix = cube[:, beta, alpha] / pixel_area_arcsec / dwave / 25  # in photon/s/m^2/microns

    signal_mJy = flux.photon2jansky(signal_1pix, wave) * 1e3

    fig, ax = plt.subplots()

    ax.plot(wave, signal_mJy)

    ax.set_xlabel(r"Wavelength [$\mu$m]")
    ax.set_ylabel("Flux [mJy]")
    ax.set_title(r"Spectrum for pixel $(\alpha, \beta)$ = ({}, {})".format(alpha, beta))

    return fig, wave, signal_mJy


def histogram(data, xlabel, title=None):
    """
    Histogram of input data with nb bins optimized for the given data
    Histogram is normalized by default

    :param data:
    :param str xlabel: Description of the data
    :param str title: [optional] Title for the figure

    :return: return the figure
    :rtype: Matplotlib.Figure
    """
    fig, ax = plt.subplots(figsize=(10, 7.5))

    ax.hist(data, bins=utils.optimum_nbins(data), density=True, histtype="step")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Probability distribution")

    if title is not None:
        fig.suptitle(title)

    return fig


def make_box(center, width, height, **kwargs):
    """
    Create a patches.Rectangle. The only difference is we use the center instead of the lower left corner

    All extra parameters will
    be passed to the Rectangle object

    :param center: (x,y) position of the box center
    :type center: tuple(float, float)
    :param float width: rectangle width
    :param float height: rectangle height


    :return:
    """
    half_width = width / 2
    half_height = height / 2
    lower_left_x = center[0] - half_width
    lower_left_y = center[1] - half_height
    lower_left = (lower_left_x, lower_left_y)
    box = mpatches.Rectangle(lower_left, width, height, **kwargs)

    return box


def MIRI_flag_images(filenames, flag=2, titles=None, title_keyword=None):
    """
    Given level 2 files, (cal or rates) will display the DQ image of one given flag for each file
    By default, will be the Saturation flag (2^1=2 ; flag=1)

    :param list(str) filenames: List of FITS filenames (or just one filename as a str)
    :param int flag: [optional] Display saturation by default. If set, represent the flag value. Can be a pure flag
                                (2) or a combination of multiple flags (5 = 4+1)

    :param list(str) titles: [optional] If set, will be used as title for each image.
                             If title_keyword is set, this parameter is ignored.
                             If neither titles, nor title_keyword are set, the filename is used as title
    :param str title_keyword: [optional] If set, will retrieve and display the value of that
                              header keyword for each image as its title.
                              This parameter takes precedence over titles if both are set

    :return: return the figure
    :rtype: Matplotlib.Figure
    """

    if isinstance(filenames, str):
        filenames = [filenames]

    nb_plots = len(filenames)
    nb_x_plots = int(np.ceil(np.sqrt(nb_plots)))
    nb_y_plots = int(np.ceil(nb_plots / nb_x_plots))

    if titles is None:
        titles = [os.path.basename(f) for f in filenames]
    elif len(titles) != nb_plots:
        raise ValueError(f"titles must be a list with the same length as filenames")

    # If power of 2, we can get the flag meaning
    if flag & (flag - 1) == 0:
        flag_detail = constants.status_pipeline[flag]
    else:
        bits = mk.decompose_mask_status(flag)
        flag_detail = "+".join(map(str, bits))

    # Plot
    # define a figure which can contains several plots, you can define resolution and so on here...
    fig, axarr = plt.subplots(nb_y_plots, nb_x_plots, sharex='all', sharey='all', figsize=(9., 7.))

    if nb_plots > 1:
        axarr = axarr.flatten()
    else:
        axarr = [axarr]

    for i in range(nb_plots):
        file = filenames[i]
        ax = axarr[i]

        hdulist = fits.open(file)
        metadata = hdulist[0].header

        if title_keyword:
            title = f"{title_keyword} = {metadata[title_keyword]}"
        else:
            title = titles[i]

        # Create a masked array
        mask = hdulist['DQ'].data

        flag_image = mk.extract_flag_image(mask, flag)

        ax.imshow(flag_image, cmap='Greys_r', origin="lower")
        ax.set_title(title)

    # Delete extra plots
    for j in range(i+1, len(axarr)):
        fig.delaxes(axarr[j])

    for int_i in range(0, nb_plots, nb_x_plots):
        axi = axarr[int_i]
        axi.set_ylabel("Y pixels")

    for int_i in range(nb_plots - nb_x_plots, nb_plots):
        axi = axarr[int_i]
        axi.set_xlabel("X pixels")

    fig.suptitle(f"Flag: {flag_detail} (Black=Not flagged ; White=flagged)")

    return fig



def MIRI_flag_identifier(filename, flags=None):
    """
    Used to study flags and find what flag is causing one specific part of the image to be masked

    :param str filename: Filename of the FITS file to read
    :param list(int) flags: [optional] Display all flags in individual images by default. If you only want of subset, 
    provide a list of those flags (e.g. [1, 2, 4]). WARNING: Must be a power of 2 (i.e individual flag)

    :return: return the figure
    :rtype: Matplotlib.Figure
    """
    if flags is None:
        flags = [2**i for i in range(32)]

    nb_plots = len(flags) + 1 # One extra plot for the image
    nb_x_plots = int(np.ceil(np.sqrt(nb_plots)))
    nb_y_plots = int(np.ceil(nb_plots / nb_x_plots))

    hdulist = fits.open(filename)
    image = hdulist["SCI"].data

    # Create a masked array
    mask = hdulist['DQ'].data

    indiv_masks = mk.get_separated_dq_array(mask)

    # For all requested flag, we need the corresponding power of 2
    power_of_2s = []
    for flag in flags:
        power_of_2 = int(np.log10(flag)/np.log10(2))
        power_of_2s.append(power_of_2)

    # Plot
    # define a figure which can contains several plots, you can define resolution and so on here...
    fig, axarr = plt.subplots(nb_y_plots, nb_x_plots, sharex='all', sharey='all', figsize=(12., 10.))
    fig.subplots_adjust(left=0.08, bottom=0.1, right=0.96, top=0.9, wspace=0.1, hspace=0.3)

    if nb_plots > 1:
        axarr = axarr.flatten()
    else:
        axarr = [axarr]

    # Plot of actual image first, for easier zoom
    ax = axarr[0]

    zscale = interval.ZScaleInterval(n_samples=600, contrast=0.25, max_reject=0.5, min_npixels=5, krej=2.5,
                                     max_iterations=5)

    (vmin, vmax) = zscale.get_limits(image)

    normalization = colors.Normalize(vmin=vmin, vmax=vmax)  # Linear

    ax.imshow(image, origin='lower', norm=normalization, cmap="viridis")
    ax.set_title("Image")

    for i in range(1, nb_plots):

        power_of_2 = power_of_2s[i-1]  # First plot is actual image
        flag = 2**power_of_2
        ax = axarr[i]
        title = f"Flag: {flag}"  # Not using detail because too long and too many plots  ({constants.status_pipeline[flag]})

        ax.imshow(indiv_masks[:, :, power_of_2], cmap='Greys_r', origin="lower")
        ax.set_title(title)

    # Delete extra plots
    for j in range(i+1, len(axarr)):
        fig.delaxes(axarr[j])

    for int_i in range(0, nb_plots, nb_x_plots):
        axi = axarr[int_i]
        axi.set_ylabel("Y pixels")

    for int_i in range(nb_plots - nb_x_plots, nb_plots):
        axi = axarr[int_i]
        axi.set_xlabel("X pixels")

    fig.suptitle(f"Flag images for {os.path.basename(filename)} (Black=Not flagged ; White=flagged)")

    # fig2, ax2 = plt.subplots()

    # y = len(power_of_2s)+1
    # for power_of_2 in power_of_2s:
    #     flag = 2**power_of_2
    #     text = f"Flag {flag} (2**{power_of_2}): {constants.status_pipeline[flag]}"
    #     ax2.text(0, y, text)
    #     y -= 1

    fig2 = plt.figure(figsize=(10, 7.5))
    # text = fig2.text(0.5, 0.5, 'Hello path effects world!\nThis is the normal '
    #                           'path effect.\nPretty dull, huh?',
    #                 ha='center', va='center', size=20)
    y = 0.9
    for power_of_2 in power_of_2s:
        flag = 2**power_of_2
        text = f"Flag {flag} (2**{power_of_2}): {constants.status_pipeline[flag]}"
        fig2.text(0.1, y, text)
        y -= 0.025
    plt.show()

    # ax2.set_axis_off() # We only care about text, hide axis and border

    return fig


def MIRI_saturation_frame(ramp_image, frame_to_plot=None, sat_limit=62000, filename=None, vmin=None, vmax=None):
    """
    Display at which frame each pixel start to saturate

    :param ramp_image: Ramp image i.e raw data (only one integration accepted)
    :type ramp_image: np.array(n_frames, y, x) or np.array(1, n_frames, y, x)
    :param int frame_to_plot: [Optional] What frame index do you want to plot for the reference image (left plot)?
                              By default, last frame is used
    :param int sat_limit: Saturation limit you want to use. By default 62000 is used
    :param str filename: [Optional] Filename for the output file if you want to save it
    :param float vmin: [optional] If set, will limit the Vrange to focus on a subset of frames to look for partial
    saturation.
    :param float vmax: [optional] If set, will limit the Vrange to focus on a subset of frames to look for partial
    saturation.

    :return: return the figure
    :rtype: Matplotlib.Figure
    """

    # Get rid of the 4th dimension if we pass a ramp cube with only one integration
    ramp_image = ramp_image.squeeze()

    if ramp_image.ndim == 4:
        ramp_image = np.mean(ramp_image, axis=1)

    (n_frames, ny, nx) = ramp_image.shape

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12., 6.), sharex=True, sharey=True)
    fig.subplots_adjust(left=0, right=1, wspace=0.1)

    if frame_to_plot is None:
        frame_to_plot = n_frames - 1
    else:
        if frame_to_plot < 0:
            frame_to_plot = n_frames + frame_to_plot

        if frame_to_plot >= n_frames:
            raise ValueError(f"frame_to_plot ({frame_to_plot}) can't be bigger than ramp length (Nframes={n_frames})")

    image_to_plot = ramp_image[frame_to_plot, :, :]
    LOG.debug(f"Max signal value in data (frame = {frame_to_plot+1}) - {np.max(image_to_plot)}")

    # True if that particular frame is saturated. Display True up until a given frame number of each pixel
    saturation_mask = ramp_image >= sat_limit
    frame_calc = np.argmax(saturation_mask, axis=0) + 1  # frame number = index + 1

    # Mask unsaturated pixels for the plot
    no_saturation_mask = ramp_image[-1, :, :] < sat_limit
    masked_array = np.ma.masked_where(no_saturation_mask, frame_calc)
    
    kwargs = {}
    
    if vmax is not None:
        kwargs["vmax"] = vmax
    
    if vmin is not None:
        kwargs["vmin"] = vmin

    cs = ax1.imshow(image_to_plot, origin='lower', cmap="viridis")
    cs2 = ax2.imshow(masked_array, origin='lower', cmap="Set1", **kwargs)

    cbar = fig.colorbar(cs, ax=ax1)
    cbar.set_label("Signal [DN]")
    ax1.set_title(f"Detector signal at frame {frame_to_plot+1} / {n_frames}")
    ax1.set_xlabel("X [Pixel]")
    ax1.set_ylabel("Y [Pixel]")

    cbar2 = fig.colorbar(cs2, ax=ax2)
    cbar2.set_label(f"Frame Number")
    ax2.set_title(f"First saturated (DN > {sat_limit}) frame (white = No saturation)")
    ax2.set_xlabel("X [Pixel]")
    ax2.set_ylabel("Y [Pixel]")

    if filename:
        fig.savefig(filename)

    return fig


def MIRI_ramp_flag(filename, flag=2):
    """
    Given level 2 files, (cal or rates) will display the DQ image of one given flag for each file
    By default, will be the Saturation flag (2^1=2 ; flag=1)

    :param list(str) filenames: List of FITS filenames (or just one filename as a str)
    :param int flag: [optional] Display saturation by default. If set, represent the flag value. Can be a pure flag
                                (2) or a combination of multiple flags (5 = 4+1)

    :param list(str) titles: [optional] If set, will be used as title for each image.
                             If title_keyword is set, this parameter is ignored.
                             If neither titles, nor title_keyword are set, the filename is used as title
    :param str title_keyword: [optional] If set, will retrieve and display the value of that
                              header keyword for each image as its title.
                              This parameter takes precedence over titles if both are set

    :return: return the figure
    :rtype: Matplotlib.Figure
    """
    hdulist = fits.open(filename)
    sample_image = hdulist[1].data[0,-1,:,:]

    groupdq = hdulist[3].data

    (nints, ngroups, ny, nx) = groupdq.shape

    header = hdulist[0].header

    nb_plots = nints + 1
    nb_x_plots = int(np.ceil(np.sqrt(nb_plots)))
    nb_y_plots = int(np.ceil(nb_plots / nb_x_plots))
    
    titles = [f"Int {i+1}" for i in range(nints)]
    titles.insert(0, "Image")

    # If power of 2, we can get the flag meaning
    if flag & (flag - 1) == 0:
        flag_detail = constants.status_pipeline[flag]
    else:
        bits = mk.decompose_mask_status(flag)
        flag_detail = "+".join(map(str, bits))

    # Plot
    # define a figure which can contains several plots, you can define resolution and so on here...
    fig, axarr = plt.subplots(nb_y_plots, nb_x_plots, sharex='all', sharey='all', figsize=(9., 7.))
    fig.subplots_adjust(left=0.12, bottom=0.1, right=0.96, top=0.9, wspace=0.1, hspace=0.26)

    if nb_plots > 1:
        axarr = axarr.flatten()
    else:
        axarr = [axarr]
    
    # todo   
    ax = axarr[0]
    ax.imshow(sample_image, origin='lower', cmap="viridis")

    # I have to make the full flag image myself because it's too big when I try to get it in one go
    full_flags = np.zeros_like(groupdq)

    for i in range(nints):
        int_mask = groupdq[i-1]  # i is the plot index, and the first one is the image, not the integration; so we are
        # shifted by one

        flag_image = mk.extract_flag_image(int_mask, flag)
        full_flags[i] = flag_image

    # True if that particular frame is saturated. Display True up until a given frame number of each pixel
    frame_calc = np.argmax(full_flags, axis=1) + 1  # frame number = index + 1

    # Mask pixels not flagged at all for the plot
    no_saturation_mask = np.sum(full_flags, axis=1) == 0
    del full_flags
    masked_array = np.ma.masked_where(no_saturation_mask, frame_calc)

    vmin = np.min(frame_calc)
    vmax = np.max(frame_calc)

    kwargs = {}
    kwargs["vmax"] = vmax
    kwargs["vmin"] = vmin

    for i in range(1, nb_plots):
        ax = axarr[i]
        title = titles[i]

        cs2 = ax.imshow(masked_array[i-1], origin='lower', cmap="Set1", **kwargs)

        ax.set_title(title)

    # Delete extra plots
    for j in range(i + 1, len(axarr)):
        fig.delaxes(axarr[j])

    # Display the colorbat only once for all integrations since we did the same vrange
    cbar2 = fig.colorbar(cs2, ax=fig.get_axes())
    cbar2.set_label(f"Frame Number")

    for int_i in range(0, nb_plots, nb_x_plots):
        axi = axarr[int_i]
        axi.set_ylabel("Y pixels")

    for int_i in range(nb_plots - nb_x_plots, nb_plots):
        axi = axarr[int_i]
        axi.set_xlabel("X pixels")

    fig.suptitle(f"First occurence of flag in integration: {flag_detail}")

    return fig

def _add_arrow_to_line2D(axes, line, arrow_locs=[0.2, 0.4, 0.6, 0.8], arrowstyle='-|>', arrowsize=1, transform=None):
    """
    Add arrows to a matplotlib.lines.Line2D at selected locations.

    source: https://stackoverflow.com/questions/26911898/matplotlib-curve-with-arrow-ticks

    Parameters:
    -----------
    axes:
    line: Line2D object as returned by plot command
    arrow_locs: list of locations where to insert arrows, % of total length
    arrowstyle: style of the arrow
    arrowsize: size of the arrow
    transform: a matplotlib transform instance, default to data coordinates

    Returns:
    --------
    arrows: list of arrows
    """
    if not isinstance(line, mlines.Line2D):
        raise ValueError("expected a matplotlib.lines.Line2D object")
    x, y = line.get_xdata(), line.get_ydata()

    arrow_kw = {
        "arrowstyle": arrowstyle,
        "mutation_scale": 10 * arrowsize,
    }

    color = line.get_color()
    use_multicolor_lines = isinstance(color, np.ndarray)
    if use_multicolor_lines:
        raise NotImplementedError("multicolor lines not supported")
    else:
        arrow_kw['color'] = color

    linewidth = line.get_linewidth()
    if isinstance(linewidth, np.ndarray):
        raise NotImplementedError("multiwidth lines not supported")
    else:
        arrow_kw['linewidth'] = linewidth

    if transform is None:
        transform = axes.transData

    arrows = []
    for loc in arrow_locs:
        s = np.cumsum(np.sqrt(np.diff(x) ** 2 + np.diff(y) ** 2))
        n = np.searchsorted(s, s[-1] * loc)
        arrow_tail = (x[n], y[n])
        arrow_head = (np.mean(x[n:n + 2]), np.mean(y[n:n + 2]))
        p = mpatches.FancyArrowPatch(
            arrow_tail, arrow_head, transform=transform,
            **arrow_kw)
        axes.add_patch(p)
        arrows.append(p)
    return arrows


def compare_dithers(dithers, labels, xlabel=None, ylabel=None):
    """
    Display dither patterns given as pixel positions (relative or not)

    :param dithers: list of tuple (x's, y's) for each of the patterns. If only one label is provided, assume only one
                    dither is provided as a single tuple, instead of a list of tuples
    :type dithers: list(tuple(list(x), list(y))) or if only one dither: tuple(list(x), list(y))
    :param labels: Pattern names, One for each dither pattern provided above
    :type labels: list(str) or str if only one dither
    :param str xlabel: [Optional] By default, in pixel, if you want another label you can specify it here
    :param str ylabel: [Optional] By default, in pixel, if you want another label you can specify it here

    :return: return the figure
    :rtype: Matplotlib.Figure
    """
    if xlabel is None:
        xlabel = "X [pixels]"

    if ylabel is None:
        ylabel = "Y [pixels]"

    fig, ax = plt.subplots(figsize=(10, 7.5))

    if isinstance(labels, str):
        labels = [labels]
        dithers = [dithers]

    if len(dithers) != len(labels):
        raise ValueError(f"dithers and labels must have the same length.")

    for label_name, (dx, dy) in zip(labels, dithers):

        line, = ax.plot(dx, dy, "+-", label=label_name)

        if len(dx) > 1:
            _add_arrow_to_line2D(ax, line, arrowstyle='->', arrowsize=2)

    ax.legend()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_aspect("equal")

    return fig


def pixel_ramps(ramp_image, metadata, pixel, filename=None, substract_first=True):
    """
    Plots all ramps in one exposure for a given pixel. First frame value is substracted so all ramps start from the
    same point.

    :param ramp_image: Ramp image for one exposure
    :type ramp_image: ndarray(nints, nframes, y, x)
    :param dict metadata: Metadata as dictionnary from 1st extension
    :param pixel: Pixel coordinates (x, y) (FITS convention, lower leftmost pixel is (1,1))
    :type pixel: tuple(int, int)
    :param str filename: savefig filename for plot
    :param bool substract_first: [default=True] Will substract first frame to all ramps to make sure we can compare
    them. But if you care about saturation, you might not want to do that.

    :return: return the figure
    :rtype: Matplotlib.Figure
    """

    # Plot
    fig, ax = plt.subplots(figsize=(14., 8.))  # size in inches
    fig.subplots_adjust(left=0.06, bottom=0.1, right=0.97, top=0.92, wspace=0.1, hspace=0.22)

    nints, ngroups, ny, nx = ramp_image.shape

    x_p = pixel[0] - 1
    y_p = pixel[1] - 1

    if x_p < 0:
        raise ValueError("Pixel x coordinate can't be lower than 0")

    if y_p < 0:
        raise ValueError("Pixel y coordinate can't be lower than 0")

    ramps = ramp_image[:, :, y_p, x_p]

    ylabel = "Signal [DN]"

    # Substract first frame on each ramp
    if substract_first:
        ramps = ramps - ramps[:, 0, np.newaxis]
        ylabel += " (First frame substracted)"

    times = np.arange(ngroups) * metadata["TGROUP"]

    nints = metadata["NINTS"]
    plot_colors = plt.cm.nipy_spectral(np.linspace(0, 1, nints))

    for i, ramp in enumerate(ramps):
        int_color = plot_colors[i]

        ax.plot(times, ramp, marker="o", markersize=2, color=int_color, linestyle="-", label=f"Integration {i+1}")

    ax.legend()

    ax.xaxis.grid(True, which='major', color='#000000', linestyle='--')
    ax.yaxis.grid(True, which='major', color='#000000', linestyle='--')
    ax.set_xlabel("Time [s]")


    ax.set_ylabel(ylabel)

    fig.suptitle(f"Plot all integration for pixel (x, y) = {pixel}")

    if filename is not None:
        fig.savefig(filename)

    return fig
