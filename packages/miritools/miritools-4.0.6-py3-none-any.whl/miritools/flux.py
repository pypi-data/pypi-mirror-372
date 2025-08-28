"""
Convert magnitude in a given band to a flux, and vice-versa

For a simple definition, see
https://www.gnu.org/software/gnuastro/manual/html_node/Magnitude-to-flux-conversion.html
magnitude = -2.5 log10(Flux/Flux0)
Flux0 is the zero point.

Source for zero-point values:
http://ssc.spitzer.caltech.edu/warmmission/propkit/pet/magtojy/ref.html

date:  10 avr 2020
Author: Rene Gastaud & Christophe Cossou, CEA

"""

import numpy as np
from astropy import units as u
from astropy.modeling import models

import logging

from . import constants

LOG = logging.getLogger(__name__)


def get_band_info(band, system):
    """
    Retrieve information on a given band in a dictionnary 'band_info' that need to be
    available in global variable of the script at this level.

    :param str band: Band name (e.g. V for Johnson)
    :param str system: possible values: Johnson, 2MASS, UKIRT, MARLIN)
    :return: wref in microns and zeropoint in Jy
    :rtype: tuple(Quantity, Quantity)
    """

    system_list = ["Johnson", "2MASS", "UKIRT", "MARLIN"]

    if system not in system_list:
        LOG.info(f"Unknown system '{system}'. Possible values: {system_list}")
        return None, None

    key = f"{system} {band}"

    try:
        band_dict = constants.band_info[key]
        zeropoint = band_dict["zeropoint"]
        wref = band_dict["wref"]
    except KeyError:
        bands = [k.split()[1] for k in constants.band_info.keys() if system in k]
        LOG.info(f"Unknown band '{band}' for '{system}'. Available bands are: {', '.join(bands)}")
        return None, None

    return wref * u.micron, zeropoint * u.Jy


def flux2mag(flux, band, system="Johnson"):
    """
    Convert flux in mJy to magnitude in a given band. Flux need to be adjusted to the central wref of that band

    :param float flux: flux in mJy
    :param str band: band name (e.g 'V' or Johnson system)
    :param str system: (By default Johnson, possible values: Johnson, 2MASS, UKIRT, MARLIN)
    :return: magnitude
    :rtype: float
    """

    wref, zero_point = get_band_info(band, system)

    magnitude = -2.5 * np.log10(flux * u.mJy / zero_point)

    LOG.debug(f"Flux: {flux} mJy at {wref} microns -> Magnitude {magnitude:.1f} in {system} band {band}")

    return magnitude


def mag2flux(magnitude, band, system="Johnson"):
    """
    Convert magnitude in a given band/system into flux in mJy (and return the corresponding wavelength reference

    :param float magnitude: magnitude in a given bandpass
    :param str band: band name (e.g 'V' or Johnson system)
    :param str system: (By default Johnson, possible values: Johnson, 2MASS, UKIRT, MARLIN)
    :return: flux in mJy and wref in microns
    :rtype: tuple(float, float)
    """

    wref, zero_point = get_band_info(band, system)

    flux = zero_point * 10.0 ** (-0.4 * magnitude)

    LOG.debug(f"Magnitude {magnitude} in {system} band {band} -> Flux: {flux} at {wref} microns")

    return flux.to(u.mJy).value, wref.value


def extrapolate_flux(flux, wref, waves, temperature_star):
    """
    From a flux and reference wavelength, will return the flux for other wavelength
    (using the star effective temperature for the spectrum shape)

    To convert magnitude flux in a band, use one of the following website for instance:
    - http://ssc.spitzer.caltech.edu/warmmission/propkit/pet/magtojy/
    - https://www.gemini.edu/sciops/instruments/midir-resources/imaging-calibrations/fluxmagnitude-conversion

    :param float flux: Star flux in mJy
    :param float wref: reference wavelength (microns) corresponding to the flux given in parameter
    :param waves: list of wavelengths you want to extrapolate the star flux on.
    :type waves: float or list(float) or np.array(float)
    :param float temperature_star: star effective temperature in K
    :return: flux values for all required wavelengths. Unit will be the unit of the input flux
    :rtype: quantity or np.array(quantity)
    """
    flux = flux * u.mJy
    wref = wref * u.micron
    waves = waves * u.micron

    bb_star = models.BlackBody(temperature_star * u.K)

    extrapolated_flux = flux * bb_star(waves) / bb_star(wref)

    LOG.debug(f"Assuming T={temperature_star} K, Flux: {flux} at {wref} -> Flux: {extrapolated_flux} at {waves}")

    return extrapolated_flux


def photon2jansky(flux, wave, invert=False):
    """
    Convert flux from Jansky to photon/s/pixel/micron and viceversa

    We use MIRI pixel size (pitch=25 micron so pixel area is (25e-6)**2

    photon2jansky = 1e32 * h * lambda_0 * p
    with p: flux in photon
         lambda_0 wavelenght in meter
         h: planck constant, equal to; 6.62607015 Js

    Online took for checks: https://colortool.stsci.edu/unit-conversion/#output
    NOTE: This doesn't exactly give the same result, I suppose they don't have the same definition of the planck constant

    Note also that photon/cm2/s/Angstrom = 1e8 * photon/m2/s/microns

    :param flux: Flux in photon/s/pixel/micron (or Jansky if invert=True)
    :type flux: np.array(float)
    :param wave: wavelength in microns
    :type wave: np.array(float)
    :param bool invert: If True, do jansky2photon instead

    :return: flux converted to Jansky (or photon/s/pixel/micron if invert=True)
    :rtype: np.array(float)
    """

    jansky_unit = u.Jy
    photon_unit = u.photon / u.m**2 / u.s / u.micron

    if invert:
        out_flux = (flux * jansky_unit).to(photon_unit, equivalencies=u.spectral_density(wave*u.micron))
    else:
        out_flux = (flux * photon_unit).to(jansky_unit, equivalencies=u.spectral_density(wave*u.micron))

    return out_flux.value


def jansky2photon(flux, wave):
    """
    Convert flux from Jansky to photon/s/pixel/micron

    jansky2photon = 1e32 * h * lambda_0 * p
    with p: flux in photon
    lambda_0 wavelength in meter
    h: planck constant, equal to; 6.62607015 Js

    Online took for checks: https://colortool.stsci.edu/unit-conversion/#output
    NOTE: This doesn't exactly give the same result, I suppose they don't have the same definition of the planck constant

    Note also that photon/cm2/s/Angstrom = 1e8 * photon/m2/s/microns

    :param flux: Flux in Jansky
    :type flux: np.array(float)
    :param wave: wavelength in microns
    :type wave: np.array(float)

    :return: flux converted photon/s/pixel/micron
    :rtype: np.array(float)
    """
    return photon2jansky(flux, wave, invert=True)