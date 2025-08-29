import numpy as np

# Python translation of
# https://github.com/TRIQS/triqs/blob/3.0.x/c%2B%2B/triqs/utility/pade_approximants.hpp#L72
class PadeApproximant(object):
    def __init__(self, z_in, u_in):
        N = z_in.size
        self._z_in = z_in.astype(np.complex128)
        self._a = np.zeros(N, dtype=np.complex128)

        # Change the default precision of GMP floats.
        g = np.zeros((N, N), dtype=np.complex128)
        g[0, :] = u_in

        for p in range(1,N):
            # If |g| is very small, the continued fraction should be truncated.
            if (g[p - 1, p - 1].real**2 + g[p - 1, p - 1].imag**2 < 1.0e-20):
                break

            for j in range(p, N):
                x = g[p - 1, p - 1] / g[p - 1, j] - 1.
                y = z_in[j] - z_in[p - 1]
                g[p, j] = x / y

        for j in range(N):
            self._a[j] = g[j, j]


    # give the value of the pade continued fraction at complex number e
    def __call__(self, e):
        if np.isscalar(e):
            return self._eval_vec([e])[0]
        else:
            return self._eval_vec(e)

    def _eval_vec(self, evec):
        evec = np.asarray(evec)
        assert isinstance(evec, np.ndarray)
        nvec = evec.size
        A1 = np.zeros(nvec, dtype=np.complex128)
        A2 = np.full(nvec, self._a[0])
        B1 = np.ones(nvec, dtype=np.complex128)
        N = self._a.size
        for i in range(N - 1):
            Anew = A2 + (evec - self._z_in[i]) * self._a[i + 1] * A1
            Bnew = 1.0 + (evec - self._z_in[i]) * self._a[i + 1] * B1
            A1            = A2 / Bnew
            A2            = Anew / Bnew
            B1            = 1.0 / Bnew
        return A2
