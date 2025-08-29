from jax import Array
from jax.typing import ArrayLike
import jax.numpy as jnp
import jax_cosmo as jc

from .cosmology import G
from . import cosmology


class NFWHalo:
    """
    Properties of a dark matter halo following a Navarro-Frenk-White
    density profile.

    Parameters
    ----------
    m_delta: float
        Mass at overdensity `delta` [h-1 Msun]
    c_delta: float
        Concentration at overdensity `delta`
    z: float
        Redshift
    cosmo: jc.Cosmology
        Underlying cosmology
    delta: float
        Density contrast in units of critical density at redshift z,
        defaults to 200.
    """

    def __init__(
        self,
        m_delta: ArrayLike,
        c_delta: ArrayLike,
        z: ArrayLike,
        cosmo: jc.Cosmology,
        delta: float = 200.0,
    ):
        self.m_delta = jnp.asarray(m_delta)
        self.c_delta = jnp.asarray(c_delta)
        self.z = jnp.asarray(z)
        self.delta = delta
        self.cosmo = cosmo

        mean_rho = delta * cosmology.critical_density(self.z, cosmo)
        self.Rdelta = (3 * self.m_delta / (4 * jnp.pi * mean_rho)) ** (1 / 3)
        self.Rs = self.Rdelta / self.c_delta
        rho0_denum = 4 * jnp.pi * self.Rs**3
        rho0_denum *= jnp.log(1 + self.c_delta) - self.c_delta / (
            1 + self.c_delta
        )
        self.rho0 = self.m_delta / rho0_denum

    def density(self, r: ArrayLike) -> Array:
        """NFW density profile :math:`\\rho(r)`.

        Parameters
        ----------
        r : Array [h-1 Mpc]
            Radius

        Returns
        -------
        Array [h2 Msun Mpc-3]
            Density at radius `r`
        """
        r = jnp.asarray(r)
        return self.rho0 / (r / self.Rs * (1 + r / self.Rs) ** 2)

    def enclosed_mass(self, r: ArrayLike) -> Array:
        """Enclosed mass profile :math:`M(<r)`.

        Parameters
        ----------
        r : Array [h-1 Mpc]
            Radius

        Returns
        -------
        Array [h-1 Msun]
            Enclosed mass at radius `r`
        """
        r = jnp.asarray(r)
        prefact = 4 * jnp.pi * self.rho0 * self.Rs**3
        return prefact * (jnp.log(1 + r / self.Rs) - r / (r + self.Rs))

    def potential(self, r: ArrayLike) -> Array:
        """Potential profile :math:`\\phi(r)`.

        Parameters
        ----------
        r : Array [h-1 Mpc]
            Radius

        Returns
        -------
        Array [km2 s-2]
            Potential at radius `r`
        """
        r = jnp.asarray(r)
        # G = G.to("km2 Mpc Msun-1 s-2").value
        prefact = -4 * jnp.pi * G * self.rho0 * self.Rs**3
        return prefact * jnp.log(1 + r / self.Rs) / r
