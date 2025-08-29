import importlib.resources as importlib_resources
from pathlib import Path
from typing import cast

import matplotlib as mpl


def scale_mpl(scaling: float) -> None:
    # Scale all the parameters by the same factor depending on the level
    # this heavily borrows from seaborn.set_context (v0.11.1) see
    # https://github.com/mwaskom/seaborn/blob/a41703e7fddf8f66b1fd5f994f983b37e865a3b2/seaborn/rcmod.py#L439
    # https://github.com/mwaskom/seaborn/blob/a41703e7fddf8f66b1fd5f994f983b37e865a3b2/seaborn/rcmod.py#L338

    # Set up dictionary of default parameters
    texts_base_context = {
        "font.size": 12,
        "axes.labelsize": 12,
        "axes.titlesize": 12,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "legend.fontsize": 11,
        "legend.title_fontsize": 12,
    }

    base_context = {
        "axes.linewidth": 1.25,
        "grid.linewidth": 1,
        "lines.linewidth": 1.5,
        "lines.markersize": 6,
        "patch.linewidth": 1,
        "xtick.major.width": 1.25,
        "ytick.major.width": 1.25,
        "xtick.minor.width": 1,
        "ytick.minor.width": 1,
        "xtick.major.size": 6,
        "ytick.major.size": 6,
        "xtick.minor.size": 4,
        "ytick.minor.size": 4,
    }
    base_context.update(texts_base_context)

    context_dict = {k: v * scaling for k, v in base_context.items()}

    # the reason why the scaling are separated comes
    # from seaborn where the font sizes are controlled
    # by an independent factor, so I'm keeping the structure
    # in case we want to do that as well later
    font_dict = {k: context_dict[k] * scaling for k in texts_base_context}
    context_dict.update(font_dict)
    mpl.rcParams.update(context_dict)


def set_mpl_style(scaling: float) -> None:
    if mpl.__version_info__ >= (3, 7):
        import matplotlib.style

        matplotlib.style.use("nonos.default")
    else:
        # promise mypy this is a Path to get around a broad return type
        # from importlib_resource.files
        nonos_path = cast(Path, importlib_resources.files("nonos"))
        mpl.rc_file(nonos_path / "default.mplstyle")
    scale_mpl(scaling)
