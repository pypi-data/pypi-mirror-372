import numpy as np
import pyshtools as sh
import pytest

from spherical_harmonic_inversion import (
    SphericalHarmonicsUtils,
    InversionData,
    SphericalHarmonicInversion,
)

def test_vector_roundtrip():
    # Create a synthetic SHCoeffs with known values
    clm = sh.SHCoeffs.from_zeros(lmax=5, normalization="ortho", csphase=-1)
    clm.set_coeffs(ls=2, ms=1, values=42)
    coeffs = SphericalHarmonicsUtils.clm_to_vector(clm)
    clm_back = SphericalHarmonicsUtils.vector_to_clm(coeffs)

    # Round-trip consistency
    np.testing.assert_allclose(clm.to_array(), clm_back.to_array(), atol=1e-10)


def test_inversion_data_loading(tmp_path):
    # Create a small synthetic dataset
    file = tmp_path / "synthetic.xyz"
    np.savetxt(file, np.array([
        [0, 0, 10, 1],
        [90, 45, 20, 2],
    ]))

    data = InversionData(str(file))
    assert data.n_obs == 2
    assert np.allclose(data.colat, [90, 45])


def test_synthetic_inversion():
    # Define known SH field (l=2, m=0 with amplitude 1.23)
    l_max = 40
    rng = np.random.default_rng()
    ls = [rng.integers(1, l_max+1) for _ in range(10)]
    ms = [rng.integers(-l, l+1) for l in ls]
    values = rng.uniform(-2, 2, len(ls))
    true_clm = sh.SHCoeffs.from_zeros(lmax=l_max, normalization="ortho", csphase=-1)

    true_clm.set_coeffs(ls=ls, ms=ms, values=values)

    # Observation points
    obs_fname = "/space/ij264/earth-tunya/data/2024/global_holdt.xyz"
    data = np.loadtxt(obs_fname)
    lon = data[:, 0]
    lat = data[:, 1]
    colat = 90 - lat
    n_obs = data.shape[0]

    # Forward evaluate the SH field at obs points
    obs = sh.expand.MakeGridPoint(true_clm.coeffs, lat, lon, l_max, 4, -1)

    # Add small noise
    noise = rng.normal(0, 1e-6, size=n_obs)
    obs_noisy = obs + noise
    error = np.ones_like(obs_noisy) * 1e-6

    # Save synthetic data
    file = f'synthetic.xyz'
    np.savetxt(file, np.column_stack([lon, lat, obs_noisy, error]))

    # Build inversion (forces A recomputation)
    data = InversionData(str(file))
    inversion = SphericalHarmonicInversion(data, l_max=l_max)

    # Patch path so A gets rebuilt in tmp_path
    inversion.A = inversion._load_or_build_A()

    # Solve
    clm_recovered = inversion.solve(lambda_norm=400, lambda_grad=1)
    print(inversion.misfit)
    assert inversion.misfit < 1.