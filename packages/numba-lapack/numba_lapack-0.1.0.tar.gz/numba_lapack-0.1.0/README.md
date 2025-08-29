<p align="center">
  <picture>
    <source srcset="https://raw.githubusercontent.com/MTZ-dev/numba-lapack/main/docs/_static/logo.svg" type="image/svg+xml">
    <img src="https://raw.githubusercontent.com/MTZ-dev/numba-lapack/main/docs/_static/logo.png"
         alt="numba-lapack"
         width="180">
  </picture>
</p>

# numba-lapack

UNSAFE, zero-overhead Numba intrinsics that expose the full BLAS/LAPACK C-APIs
via SciPy’s `__pyx_capi__`. Call BLAS/LAPACK directly from `@njit` in nopython mode.

> ⚠️ **Unsafe means unsafe**: raw pointer semantics; you are responsible for valid pointers, shapes, and leading dimensions.

## Highlights

- Auto-discovers `scipy.linalg.cython_blas` and `cython_lapack` symbols at import.
- Generates Numba `@intrinsic` wrappers with the *exact* ABI (no Python overhead).
- Accepts arrays, typed pointers, or by-ref scalars for pointer parameters.
- Ships type stubs so IDEs can see function names & arg docs.

## Quick start

```python
import numpy as np
from numba import njit
from numba_lapack import dgemm

@njit(cache=True)
def gemm_nn(A, B, C, alpha, beta):
    m, k = A.shape
    _, n = B.shape
    dgemm(np.uint8(ord('N')), np.uint8(ord('N')),
          m, n, k, alpha, A, m, B, k, beta, C, m)
