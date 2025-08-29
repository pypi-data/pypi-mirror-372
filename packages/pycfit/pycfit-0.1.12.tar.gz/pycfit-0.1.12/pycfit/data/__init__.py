import numpy as np
import astropy.units as u
from pathlib import Path

def get_example_single_spectra(units=False):
    """
    Example single spectra data
    Returns a tuple: (wavelength, intensity, uncertainty) 
    
    Optional:  "units=True" will return arrays of Astropy Quantities
               intead of unit-less numpy arrays

    From Solar Orbiter mission, SPICE instrument
    Spectra from window 'O III 703 / Mg IX 706 (Merged)'
    Averaged across raster
    Source file: solo_L2_spice-n-ras_20240425T121922_V22_251658647-000.fits
    """

    LOCAL_DIR = Path(__file__).parent
    avg = np.load(LOCAL_DIR.joinpath('avg_data.npz'))

    if units:
        wavelength = avg['wavelength'] * u.Unit(str(avg['wv_unit']))
        intensity = avg['intensity'] * u.Unit(str(avg['in_unit']))
        uncertainty = avg['uncertainty'] * u.Unit(str(avg['in_unit']))
        return wavelength, intensity, uncertainty
    else:
        return avg['wavelength'], avg['intensity'], avg['uncertainty']


def get_example_grid_spectra(patch=False, units=False):
    """
    Example raster spectra data
    Returns a tuple: (wavelength, intensity, uncertainty, mask)

    Optional:
        "patch=True" will return only a 20x20 subset.
         Otherwise, full raster is returned

        "units=True" will return arrays of Astropy Quantities
        intead of unit-less numpy arrays

    From Solar Orbiter mission, SPICE instrument
    Window 'O III 703 / Mg IX 706 (Merged)'
    Source file: solo_L2_spice-n-ras_20240425T121922_V22_251658647-000.fits
    """

    LOCAL_DIR = Path(__file__).parent

    if patch:
        data = np.load(LOCAL_DIR.joinpath('patch_data.npz'))
    else:
        data = np.load(LOCAL_DIR.joinpath('grid_data.npz'))

    if units:
        wavelength = data['wavelength'] * u.Unit(str(data['wv_unit']))
        intensity = data['intensity'] * u.Unit(str(data['in_unit']))
        uncertainty = data['uncertainty'] * u.Unit(str(data['in_unit']))
        return wavelength, intensity, uncertainty, data['mask']
    else:
        return data['wavelength'], data['intensity'], data['uncertainty'], data['mask']




