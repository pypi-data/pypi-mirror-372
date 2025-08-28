from astropy.io import fits
import numpy as np
import os
import logging
import matplotlib.pyplot as plt
from astropy.visualization import interval

LOG = logging.getLogger(__name__)

from . import constants
from . import mask as mk


def write_fits(image, filename, header=None, overwrite=True):
    """
    Create and write FITS file containing images for each dither point
    with substracted reference image


    :param image: 2D image to store in the FITS file. If a MaskedArray is provided, masked values are filled with 0
    :type image: nd.array(y,x)
    :param dict header: header for the FITS file
    :type header: astropy.io.fits.Header or dict
    :param str filename: filename for the output FITS to be created
    :param bool overwrite: overwrite substracted FITS file if they exists
    """
    # Handle the special case of a maskedArray because writing to fits wouldn't work with it. Instead, we fill values
    # with 0 and replace with a standard array.
    if isinstance(image, np.ma.MaskedArray):
        image = image.filled(0)

    # Correct HIERARCH warnings by rewriting the header
    if isinstance(header, fits.Header):
        cards = header.cards
    else:
        cards = []
        for k, v in header.items():
            # Tuple mean there's a comment
            if isinstance(v, tuple):
                cards.append((k, *v))
            else:
                cards.append((k, v, ""))

    corrected_header = fits.Header()

    if header is not None:
        for (key, value, comment) in cards:
            if len(key) > 8:
                key = f"hierarch {key}"

            corrected_header[key] = (value, comment)

    hdu = fits.PrimaryHDU(image, header=corrected_header)
    hdulist = fits.HDUList([hdu])

    path = os.path.dirname(filename)
    if path and not os.path.isdir(path):
        os.makedirs(path)

    LOG.info(f"Write file '{filename}'")
    hdulist.writeto(filename, overwrite=overwrite)


def write_jwst_fits(image, filename, header=None, overwrite=True):
    """
    Create and write FITS file containing an image and metadatas
    Try to recreate a JWST MIRI datamodel, not in detail but the general architecture
    metadata will be in the primary header and image in the SCI header.


    :param image: 2D image to store in the FITS file. If a MaskedArray is provided, masked values are filled with 0
    :type image: nd.array(y,x)
    :param dict header: header for the FITS file
    :type header: astropy.io.fits.Header or dict
    :param str filename: filename for the output FITS to be created
    :param bool overwrite: overwrite substracted FITS file if they exists
    """
    # Handle the special case of a maskedArray because writing to fits wouldn't work with it. Instead, we fill values
    # with 0 and replace with a standard array.
    if isinstance(image, np.ma.MaskedArray):
        image = image.filled(0)
    
    # Correct HIERARCH warnings by rewriting the header
    if isinstance(header, fits.Header):
        cards = header.cards
    else:
        cards = []
        for k, v in header.items():
            # Tuple mean there's a comment
            if isinstance(v, tuple):
                cards.append((k, *v))
            else:
                cards.append((k, v, ""))

    corrected_header = fits.Header()

    if header is not None:
        for (key, value, comment) in cards:
            if len(key) > 8:
                key = f"hierarch {key}"

            corrected_header[key] = (value, comment)

    phdu = fits.PrimaryHDU(header=corrected_header)

    sci_hdu = fits.ImageHDU(image, name="SCI")
    err_hdu = fits.ImageHDU(name="ERR")

    fake_mask = np.zeros_like(image, dtype="uint")
    dq_hdu = fits.ImageHDU(fake_mask, name="DQ")

    hdulist = fits.HDUList([phdu, sci_hdu, err_hdu, dq_hdu])

    path = os.path.dirname(filename)
    if path and not os.path.isdir(path):
        os.makedirs(path)

    LOG.info(f"Write file '{filename}'")
    hdulist.writeto(filename, overwrite=overwrite)


def fits_thumbnail(filename, fits_extension=1, ext="jpg", out=None):
    """
    Create a thumbnail as a .png file of one extension of a fits file with Zscale

    WARNING: That extension must be 2d obviously

    :param str filename: absolute or relative path to fits file
    :param int fits_extension: [optional] extension 1 by default
    :param str ext: [optional] output bitmap extension (by default: png). If out is defined, ext is ignored.
    :param str out: [optional] output filename. Allow to write the thumbnail in a different folder and with a
    different name than the default
    """
    with fits.open(filename) as hdulist:
        image = hdulist[fits_extension].data

    if ext != "jpg" and out is not None:
        LOG.warning(f"fits_thumbnail: ext parameter is ignored when out is defined.")

    if out is None:
        basename, dummy = os.path.splitext(filename)
        image_filename = f"{basename}.{ext}"
    else:
        image_filename = out

    write_thumbnail(image, image_filename)


def write_thumbnail(image, filename):
    """
    Write an image to bitmap with a ZScale, and the same pixel resolution

    :param image:
    :param str filename: output filename (e.g. "myimage.png")
    """

    zscale = interval.ZScaleInterval(n_samples=600, contrast=0.25, max_reject=0.5, min_npixels=5, krej=2.5,
                                     max_iterations=5)
    (vmin, vmax) = zscale.get_limits(image)

    basedir = os.path.dirname(filename)
    if not os.path.isdir(basedir):
        os.makedirs(basedir)

    plt.imsave(filename, image, cmap="viridis", vmin=vmin, vmax=vmax, origin="lower")

    LOG.info(f"Write file '{filename}'")


def MIRI_flags_image(filename):
    """
    Display all flags for a single image into individual images to find what features correspond to what flag

    Will write 32 images next to the original file with postfix *_flag_i.png

    :param filename: FITS filename
    """
    nb_flags = 32

    basename, dummy = os.path.splitext(filename)

    hdulist = fits.open(filename)
    # Create a masked array
    mask = hdulist['DQ'].data

    individual_masks = mk.get_separated_dq_array(mask)

    for i in range(nb_flags):
        fig, ax = plt.subplots(figsize=(10, 7.5))

        out_filename = f"{basename}_flag_{i}.png"
        flag_detail = constants.status_pipeline[2**i]
        title = f"flag 2^{i}: {2**i}"

        flag_image = individual_masks[:, :, i]

        ax.imshow(flag_image, cmap='Greys_r', origin="lower")
        ax.set_title(title)
        ax.set_ylabel("Y pixels")
        ax.set_xlabel("X pixels")
        fig.suptitle(f"Flags {flag_detail}: (Black=Not flagged ; White=flagged)")
        fig.savefig(out_filename)
        plt.close(fig)
