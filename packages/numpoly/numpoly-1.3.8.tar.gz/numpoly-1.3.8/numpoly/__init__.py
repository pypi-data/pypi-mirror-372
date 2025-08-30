# pylint: disable=wildcard-import
"""Numpoly -- Multivariate polynomials as numpy elements."""
import logging
import os
import sys

if sys.version_info >= (3, 10):
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata

from .baseclass import ndpoly, FeatureNotSupported, PolyLike

from .align import (
    align_polynomials,
    align_exponents,
    align_indeterminants,
    align_shape,
)
from .construct import (
    polynomial,
    aspolynomial,
    clean_attributes,
    remove_redundant_coefficients,
    remove_redundant_names,
    polynomial_from_attributes,
    polynomial_from_roots,
    monomial,
    symbols,
    variable,
)
from .sympy_ import to_sympy

from .array_function import *
from .cfunctions import *
from .poly_function import *
from .utils import (
    bindex,
    cross_truncate,
    glexindex,
    glexsort,
)
from .option import get_options, set_options, global_options
from .dispatch import FUNCTION_COLLECTION, UFUNC_COLLECTION


def get_version(name: str) -> str:
    """
    Get distribution version number, if it exists.

    Example:
        >>> get_version("numpy") == ""
        False
        >>> get_version("not_an_distribution") == ""
        True

    """
    try:
        version = importlib_metadata.version(name)
    except importlib_metadata.PackageNotFoundError:
        version = ""
    return version


def configure_logging() -> None:
    """Configure logging for Numpoly."""
    logpath = os.environ.get("NUMPOLY_LOGPATH", os.devnull)
    logging.basicConfig(level=logging.DEBUG, filename=logpath, filemode="w")
    streamer = logging.StreamHandler()
    loglevel = logging.DEBUG if os.environ.get("NUMPOLY_DEBUG", "") else logging.WARNING
    streamer.setLevel(loglevel)

    logger = logging.getLogger(__name__)
    logger.addHandler(streamer)


__version__ = get_version("numpoly")
configure_logging()
