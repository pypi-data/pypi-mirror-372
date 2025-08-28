__name__ = "ICIW_Plots"
from ICIW_Plots.layout import *
from ICIW_Plots.figures import *
import matplotlib.pyplot as plt


cm2inch = 1 / 2.54
mm2inch = 1 / 25.4


def write_styles_to_configdir():
    import matplotlib as mpl
    import os
    import importlib.resources
    import glob
    import logging
    import shutil
    import warnings

    logger = logging.getLogger(__name__)
    logger.log(logging.INFO, "Trying to install ICIW styles.")
    # Find all style files
    module_dir = str(importlib.resources.files(__name__))
    stylefiles = glob.glob(module_dir + "\\*.mplstyle", recursive=True)
    logger.log(logging.INFO, stylefiles)
    # Find stylelib directory (where the *.mplstyle files go)
    mpl_stylelib_dir = os.path.join(matplotlib.get_configdir(), "stylelib")
    logger.log(logging.INFO, "Stylelib directory is: " + mpl_stylelib_dir)
    if not os.path.exists(mpl_stylelib_dir):
        logger.log(logging.INFO, "Creating stylelib directory.")
        os.makedirs(mpl_stylelib_dir)
    # Copy files over
    logger.log(logging.INFO, f"Copying styles into{mpl_stylelib_dir}")
    for stylefile in stylefiles:
        logger.log(logging.INFO, f"Copying {stylefile}")
        dest = shutil.copy(
            stylefile, os.path.join(mpl_stylelib_dir, os.path.basename(stylefile))
        )
        logger.log(logging.INFO, f"Style {stylefile} sucessfully copied to {dest}.")
    else:
        logger.log(logging.INFO, "Styles installed.")
        return

    warnings.warn("Could not install ICIW styles.")


if not "ICIWstyle" in plt.style.available:
    write_styles_to_configdir()
