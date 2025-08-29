import numpy as np
import pyshtools as sh

class SphericalHarmonicsUtils:
    """Utility functions for converting between coefficient vectors and SHCoeffs."""

    @staticmethod
    def vector_to_clm(coeffs: np.ndarray) -> sh.SHCoeffs:
        """Convert a coefficient vector into a pyshtools SHCoeffs object."""
        clm = sh.SHCoeffs.from_zeros(lmax=int(np.sqrt(len(coeffs))),
                                     normalization='ortho',
                                     csphase=-1)
        l, m = 1, -1
        for value in coeffs:
            clm.set_coeffs(ls=l, ms=m, values=value)
            if m == l:
                l += 1
                m = -l
            else:
                m += 1
        return clm

    @staticmethod
    def clm_to_vector(clm: sh.SHCoeffs) -> np.ndarray:
        """Convert an SHCoeffs object into a coefficient vector."""
        coeffs = []
        for l in range(1, clm.lmax + 1):
            for m in range(-l, 0):
                coeffs.append(clm.coeffs[1, l, np.abs(m)])
            for m in range(0, l + 1):
                coeffs.append(clm.coeffs[0, l, np.abs(m)])
        return np.array(coeffs)

def index(l: int, m: int) -> int:
    """Return the flattened index for degree l and order m."""
    return l ** 2 + l + m - 1