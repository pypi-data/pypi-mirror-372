import logging

LOG = logging.getLogger(__name__)

pixel_size = 0.11  # arcsec / pixel
jwst_mirror_diameter = 6.5  # m

# Key is JPL keyword, value is datamodel counterpart
jpl_to_datamodel = {"NINT": "NINTS",
                    "DATE_OBS": "DATE-OBS",
                    "TIME_OBS": "TIME-OBS",
                    "EXPTIME": "EFFEXPTM",
                    "INTTIME": "EFFINTTM",
                    "COLSTART": "SUBSTRT1",
                    "ROWSTART": "SUBSTRT2",
                    "NAXIS1": "SUBSIZE1",
                    "NAXIS2": "SUBSIZE2",
                    }

# wref in microns and zeropoint in Jy
band_info = {
    "2MASS J": {'wref': 1.235, 'zeropoint': 1594},
    "2MASS H": {'wref': 1.662, 'zeropoint': 1024},
    "2MASS Ks": {'wref': 2.159, 'zeropoint': 666.7},
    "Johnson U": {'wref': 0.36, 'zeropoint': 1823},
    "Johnson B": {'wref': 0.44, 'zeropoint': 4130},
    "Johnson V": {'wref': 0.55, 'zeropoint': 3781},
    "Johnson R": {'wref': 0.71, 'zeropoint': 2941},
    "Johnson I": {'wref': 0.97, 'zeropoint': 2635},
    "Johnson J": {'wref': 1.25, 'zeropoint': 1603},
    "Johnson H": {'wref': 1.60, 'zeropoint': 1075},
    "Johnson K": {'wref': 2.22, 'zeropoint': 667},
    "Johnson L": {'wref': 3.54, 'zeropoint': 288},
    "Johnson M": {'wref': 4.80, 'zeropoint': 170},
    "Johnson N": {'wref': 10.6, 'zeropoint': 36},
    "Johnson O": {'wref': 21.0, 'zeropoint': 9.4},
    "UKIRT V": {'wref': 0.5556, 'zeropoint': 3540},
    "UKIRT I": {'wref': 0.9, 'zeropoint': 2250},
    "UKIRT J": {'wref': 1.25, 'zeropoint': 1600},
    "UKIRT H": {'wref': 1.65, 'zeropoint': 1020},
    "UKIRT K": {'wref': 2.20, 'zeropoint': 657},
    "UKIRT L": {'wref': 3.45, 'zeropoint': 290},
    "UKIRT L'": {'wref': 3.80, 'zeropoint': 252},
    "UKIRT M": {'wref': 4.8, 'zeropoint': 163},
    "UKIRT N": {'wref': 10.1, 'zeropoint': 39.8},
    "UKIRT Q": {'wref': 20.0, 'zeropoint': 10.4},
    "MIRLIN N": {'wref': 10.79, 'zeropoint': 33.4},
    "MIRLIN Q-s": {'wref': 17.90, 'zeropoint': 12.4},
    "MIRLIN N0": {'wref': 7.91, 'zeropoint': 60.9},
    "MIRLIN N1": {'wref': 8.81, 'zeropoint': 49.4},
    "MIRLIN N2": {'wref': 9.69, 'zeropoint': 41.1},
    "MIRLIN N3": {'wref': 10.27, 'zeropoint': 36.7},
    "MIRLIN N4": {'wref': 11.70, 'zeropoint': 28.5},
    "MIRLIN N5": {'wref': 12.49, 'zeropoint': 25.1},
    "MIRLIN Q0": {'wref': 17.20, 'zeropoint': 13.4},
    "MIRLIN Q1": {'wref': 17.93, 'zeropoint': 12.3},
    "MIRLIN Q2": {'wref': 18.64, 'zeropoint': 11.4},
    "MIRLIN Q3": {'wref': 20.81, 'zeropoint': 9.2},
    "MIRLIN Q4": {'wref': 22.81, 'zeropoint': 7.7},
    "MIRLIN Q5": {'wref': 24.48, 'zeropoint': 6.7},
    "MIRLIN K": {'wref': 2.2, 'zeropoint': 650.0},
    "MIRLIN M": {'wref': 4.68, 'zeropoint': 165.0},
    "WISE W1": {'wref': 3.4, 'zeropoint':309.54},
    "WISE W2": {'wref': 4.6, 'zeropoint':171.787},
    "WISE W3": {'wref': 12., 'zeropoint':31.674},
    "WISE W4": {'wref': 22., 'zeropoint':8.363},
}

# DQ flags for the pipeline
# source: https://jwst-pipeline.readthedocs.io/en/latest/jwst/references_general/references_general.html#data-quality-flags
status_pipeline = {
    0: "Good pixel",
    1: "Bad pixel. Do not use.",  # 0
    2: "Pixel saturated during exposure",  # 1
    4: "Jump detected during exposure",  # 2
    8: "Data lost in transmission",  # 3
    16: "Flagged by outlier detection",  # 4
    32: "High persistence",  # 5
    64: "Below A/D floor",  # 6
    128: "Reserved",  # 7
    256: "Uncertainty exceeds quoted error",  # 8
    512: "Pixel not on science portion of detector",  # 9
    1024: "Dead pixel",  # 10
    2048: "Hot pixel",  # 11
    4096: "Warm pixel",  # 12
    8192: "Low quantum efficiency",  # 13
    16384: "RC pixel",  # 14
    32768: "Telegraph pixel",  # 15
    65536: "Pixel highly nonlinear",  # 16
    131072: "Reference pixel cannot be used",  # 17
    262144: "Flat field cannot be measured",  # 18
    524288: "Gain cannot be measured",  # 19
    1048576: "Linearity correction not available",  # 20
    2097152: "Saturation check not available",  # 21
    4194304: "Bias variance large",  # 22
    8388608: "Dark variance large",  # 23
    16777216: "Slope variance large (i.e., noisy pixel)",  # 24
    33554432: "Flat variance large",  # 25
    67108864: "Open pixel (counts move to adjacent pixels)",  # 26
    134217728: "Adjacent to open pixel",  # 27
    268435456: "Sensitive to reset anomaly",  # 28
    536870912: "Pixel sees light from failed-open shutter",  # 29
    1073741824: "A catch-all flag",  # 30
    2147483648: "Pixel is a reference pixel",  # 31
}

# Force include all flags from DQ_INIT expect bad pixels and reference pixels
include_all = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072, 262144, 524288,
               1048576, 2097152, 4194304, 8388608, 16777216, 33554432, 67108864, 134217728, 268435456, 536870912,
               1073741824]

