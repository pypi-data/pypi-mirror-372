"""
This module provides general utility functions called by code in spectrograph.
"""

import numpy as np

import astropy.units as u
from astropy import constants

from irispy.utils.constants import RADIANCE_UNIT

__all__ = [
    "calculate_photons_per_sec_to_radiance_factor",
    "convert_between_dn_and_photons",
    "convert_or_undo_photons_per_sec_to_radiance",
    "reshape_1d_wavelength_dimensions_for_broadcast",
]


def convert_between_dn_and_photons(old_data_arrays, old_unit, new_unit):
    """
    Converts arrays from IRIS DN to photons or vice versa.

    In this function, an inverse time component due to exposure time
    correction is ignored during calculations but preserved in final unit.

    Parameters
    ----------
    old_data_arrays: iterable of `numpy.ndarray`
        Arrays of data to be converted.
    old_unit: `astropy.unit.Unit`
        Unit of data arrays.
    new_unit: `astropy.unit.Unit`
        Unit to convert data arrays to.

    Returns
    -------
    `list` of `numpy.ndarray`
        Data arrays converted to new_unit.
    `astropy.unit.Unit`
        Unit of new data arrays with any inverse time component preserved.
    """
    if old_unit in [new_unit, new_unit / u.s]:
        new_data_arrays = list(old_data_arrays)
        new_unit_time_accounted = old_unit
    else:
        # During calculations, the time component due to exposure
        # time correction, if it has been applied, is ignored.
        # Check here whether the time correction is present in the
        # original unit so that is carried through to new unit.
        if u.s not in (old_unit * u.s).decompose().bases:
            old_unit_without_time = old_unit * u.s
            new_unit_time_accounted = new_unit / u.s
        else:
            old_unit_without_time = old_unit
            new_unit_time_accounted = new_unit
        # Convert data and uncertainty to new unit.
        new_data_arrays = [(data * old_unit_without_time).to(new_unit).value for data in old_data_arrays]
    return new_data_arrays, new_unit_time_accounted


def convert_or_undo_photons_per_sec_to_radiance(
    data_quantities,
    iris_response,
    obs_wavelength,
    detector_type,
    spectral_dispersion_per_pixel,
    solid_angle,
    *,
    undo=False,
):
    """
    Converts data quantities from counts/s to radiance (or vice versa).

    Parameters
    ----------
    data_quantities: iterable of `astropy.units.Quantity`
        Quantities to be converted.  Must have units of counts/s or
        radiance equivalent counts, e.g. erg / cm**2 / s / sr / Angstrom.
    iris_response: dict
        The IRIS response data loaded from `irispy.utils.response.get_latest_response`.
    obs_wavelength: `astropy.units.Quantity`
        Wavelength at each element along spectral axis of data quantities.
    detector_type: `str`
        Detector type: 'FUV', 'NUV', or 'SJI'.
    spectral_dispersion_per_pixel: scalar `astropy.units.Quantity`
        spectral dispersion (wavelength width) of a pixel.
    solid_angle: scalar `astropy.units.Quantity`
        Solid angle corresponding to a pixel.
    undo: `bool`
        If False, converts counts/s to radiance.
        If True, converts radiance to counts/s.
        Default=False

    Returns
    -------
    `list` of `astropy.units.Quantity`
        Data quantities converted to radiance or counts/s
        depending on value of undo kwarg.
    """
    # Check data quantities are in the right units.
    if undo is True:
        for i, data in enumerate(data_quantities):
            if not data.unit.is_equivalent(RADIANCE_UNIT):
                msg = (
                    "Invalid unit provided.  As kwarg undo=True, "
                    f"unit must be equivalent to {RADIANCE_UNIT}.  Error found for {i}th element "
                    f"of data_quantities. Unit: {data.unit}"
                )
                raise ValueError(
                    msg,
                )
    else:
        for data in data_quantities:
            if data.unit != u.photon / u.s:
                msg = (
                    "Invalid unit provided.  As kwarg undo=False, "
                    f"unit must be equivalent to {u.photon / u.s}.  Error found for {i}th element "
                    f"of data_quantities. Unit: {data.unit}"
                )
                raise ValueError(
                    msg,
                )
    photons_per_sec_to_radiance_factor = calculate_photons_per_sec_to_radiance_factor(
        iris_response,
        obs_wavelength,
        detector_type,
        spectral_dispersion_per_pixel,
        solid_angle,
    )
    # Change shape of arrays so they are compatible for broadcasting
    # with data and uncertainty arrays.
    photons_per_sec_to_radiance_factor = reshape_1d_wavelength_dimensions_for_broadcast(
        photons_per_sec_to_radiance_factor,
        data_quantities[0].ndim,
    )
    return (
        [(data / photons_per_sec_to_radiance_factor).to(u.photon / u.s) for data in data_quantities]
        if undo is True
        else [(data * photons_per_sec_to_radiance_factor).to(RADIANCE_UNIT) for data in data_quantities]
    )


def calculate_photons_per_sec_to_radiance_factor(
    iris_response,
    wavelength,
    detector_type,
    spectral_dispersion_per_pixel,
    solid_angle,
):
    """
    Calculates multiplicative factor that converts counts/s to radiance for
    given wavelengths.

    Parameters
    ----------
    iris_response: dict
        The IRIS response data loaded from `irispy.utils.response.get_latest_response`.
    wavelength: `astropy.units.Quantity`
        Wavelengths for which counts/s-to-radiance factor is to be calculated
    detector_type: `str`
        Detector type: 'FUV' or 'NUV'.
    spectral_dispersion_per_pixel: scalar `astropy.units.Quantity`
        spectral dispersion (wavelength width) of a pixel.
    solid_angle: scalar `astropy.units.Quantity`
        Solid angle corresponding to a pixel.

    Returns
    -------
    `astropy.units.Quantity`
        # The term "multiplicative" refers to the fact that the conversion factor calculated by the
        # `calculate_photons_per_sec_to_radiance_factor` function is used to multiply the counts per
        # second (cps) data to obtain the radiance data. In other words, the conversion factor is a
        # scaling factor that is applied to the cps data to convert it to radiance units.
        Multiplicative conversion factor from counts/s to radiance units
        for input wavelengths.
    """
    # Avoid circular imports
    from irispy.utils.response import get_interpolated_effective_area  # NOQA: PLC0415

    # Get effective area and interpolate to observed wavelength grid.
    eff_area_interp = get_interpolated_effective_area(
        iris_response,
        detector_type,
        obs_wavelength=wavelength,
    )
    # Return radiometric conversed data assuming input data is in units of photons/s.
    return (
        constants.h
        * constants.c
        / wavelength
        / u.photon
        / spectral_dispersion_per_pixel
        / eff_area_interp
        / solid_angle
    )


def reshape_1d_wavelength_dimensions_for_broadcast(wavelength, n_data_dim):
    if n_data_dim == 1:
        pass
    elif n_data_dim == 2:
        wavelength = wavelength[np.newaxis, :]
    elif n_data_dim == 3:
        wavelength = wavelength[np.newaxis, np.newaxis, :]
    else:
        msg = "IRISSpectrogram dimensions must be 2 or 3."
        raise ValueError(msg)
    return wavelength
