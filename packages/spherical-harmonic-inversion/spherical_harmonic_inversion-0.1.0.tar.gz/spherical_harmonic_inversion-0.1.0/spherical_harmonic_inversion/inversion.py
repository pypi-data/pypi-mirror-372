import numpy as np
import pyshtools as sh
import pygmt as pg
import xarray as xr
import os
from tqdm import tqdm

from .utils import index, SphericalHarmonicsUtils

class InversionData:
    """Load and store observational data for spherical harmonic inversion."""

    def __init__(self, data_file: str):
        data = np.loadtxt(data_file)
        self.lon = data[:, 0]
        self.lat = data[:, 1]
        self.colat = 90 - self.lat
        self.residual = data[:, 2]
        self.error = data[:, 3]
        self.n_obs = data.shape[0]


class SphericalHarmonicInversion:
    """
    Perform spherical harmonic inversion with Tikhonov regularization.

    Attributes:
        l_max: Maximum spherical harmonic degree.
        lambda_norm: Regularization weight for the identity term.
        lambda_grad: Regularization weight for the Laplacian term.
    """

    def __init__(self, data: InversionData, l_max: int = 40):
        # Move reg params and lmax to solve.
        # minimum degree to fit the data.

        self.data = data
        self.l_max = l_max
        self.n_coeffs = (l_max + 1) ** 2 - 1

        # Try loading A, compute if missing
        self.A = self._load_or_build_A()

        # Build regularization matrices
        self.R = np.diag([l * (l + 1)
                          for l in range(1, l_max + 1)
                          for m in range(-l, l + 1)])
        self.C_inv = np.diag(1 / self.data.error ** 2)

    def _load_or_build_A(self) -> np.ndarray:
        """Load A from file if it exists, otherwise compute and save it."""
        fname = f"/space/ij264/earth-tunya/spherical_harmonic_inversion/forward_operators/lmax_{self.l_max}/{self.data.n_obs}_observations/A.txt"
        os.makedirs(os.path.dirname(fname), exist_ok=True)
        if os.path.exists(fname):
            return np.loadtxt(fname)

        A = np.zeros((self.data.n_obs, self.n_coeffs))
        idx = 0
        for l in tqdm(range(1, self.l_max + 1), desc='Building A matrix'):
           for m in range(-l, l + 1):
               A[:, idx] = sh.expand.spharm_lm(l=l,
                                                     m=m,
                                                     normalization='ortho',
                                                     csphase=-1,
                                                     theta=self.data.colat,
                                                       phi=self.data.lon,
                                                       degrees=True)
               idx += 1

        # Save A to file for future use
        np.savetxt(fname, A)
        return A

    def solve(self, lambda_norm: float = 400, lambda_grad: float = 1) -> sh.SHCoeffs:
        """Solve the inversion system and return SHCoeffs."""
        LHS = (self.A.T @ (self.C_inv @ self.A)
               + lambda_grad * self.R
               + lambda_norm * np.eye(self.n_coeffs))
        RHS = self.A.T @ self.C_inv @ self.data.residual
        coeffs = np.linalg.solve(LHS, RHS)
        self.solution = SphericalHarmonicsUtils.vector_to_clm(coeffs)
        return self.solution

    def plot_grid(self, cmap: str = "polar", fname: str = None, l_label: int = None):
        """
        Plot the predicted field on a global grid using PyGMT.

        Args:
            cmap: Colormap to use (default "polar").
            fname: If given, save figure to this filename.
            l_label: Optional label for spherical harmonic degree shown on figure.
        """
        if not hasattr(self, "solution"):
            raise RuntimeError("Run solve() first to compute coefficients.")
        cmap = '/space/ij264/earth-tunya/cpts/coolwarm_DT.cpt'

        # Expand SH to global grid
        grid = sh.expand.MakeGrid2D(
            cilm=self.solution.coeffs,
            interval=1,
            norm=4,
            csphase=-1,
            north=90,
            south=-90,
            west=0,
            east=360,
        )

        xr_grid = xr.DataArray(
            data=grid,
            dims=["lat", "lon"],
            coords={"lat": np.arange(90, -91, -1), "lon": np.arange(0, 361)},
        )
        xr_grid.gmt.gtype = 1

        # Build figure
        fig = pg.Figure()
        fig.basemap(region="d", frame="f", projection="H12c")
        fig.grdimage(xr_grid, cmap=cmap, dpi=300)

        if l_label is not None:
            fig.text(text=f"l = {l_label}", position="BL", no_clip=True)

        fig.coast(shorelines=True, frame="f")
        fig.colorbar(
            position="JBC+o0.c/0.5c+h+e",
            frame=["x+lDynamic topography (km)"],
            cmap=cmap,
        )

        if fname:
            fig.savefig(fname, dpi=300)

    @property
    def misfit(self) -> float:
        """Calculate and return the normalized root mean square misfit."""
        if not hasattr(self, "solution"):
            raise RuntimeError("Run solve() first to compute coefficients.")
        predicted = self.A @ SphericalHarmonicsUtils.clm_to_vector(self.solution)
        residuals = self.data.residual - predicted
        misfit = np.sqrt(np.mean((residuals / self.data.error) ** 2))
        return misfit