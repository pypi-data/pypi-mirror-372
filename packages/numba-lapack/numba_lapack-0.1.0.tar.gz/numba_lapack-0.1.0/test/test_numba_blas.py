import numpy as np
import pytest
from numba import njit
from numba_lapack import daxpy, ddot, dgemv, dgemm, dgesv

@pytest.mark.parametrize("N", [1, 17, 100_003])
def test_daxpy_correct_and_strided(N):
    rng = np.random.default_rng(0)
    x = rng.standard_normal(N).astype(np.float64)
    y = rng.standard_normal(N).astype(np.float64)
    alpha = 1.75

    @njit(cache=True)
    def axpy(alpha, x, y):
        daxpy(x.size, alpha, x, 1, y, 1)

    # contiguous
    y_ref = y + alpha * x
    y2 = y.copy()
    axpy(alpha, x, y2)
    assert np.allclose(y2, y_ref, rtol=1e-12, atol=1e-12)

    # strided (views can have different lengths when N is odd)
    xs = x[::2]
    ybuf = y.copy()
    ys = ybuf[1::2]
    incx = xs.strides[0] // xs.itemsize
    incy = ys.strides[0] // ys.itemsize

    @njit(cache=True)
    def axpy_strided(alpha, xs, incx, ys, incy):
        n = min(xs.shape[0], ys.shape[0])
        daxpy(n, alpha, xs, incx, ys, incy)

    n = min(xs.shape[0], ys.shape[0])
    y_ref2 = ys.copy()
    y_ref2[:n] += alpha * xs[:n]

    axpy_strided(alpha, xs, incx, ys, incy)
    assert np.allclose(ys[:n], y_ref2[:n], rtol=1e-12, atol=1e-12)

@pytest.mark.parametrize("m,n", [(4,3), (128,64)])
def test_dgemv_N(m, n):
    rng = np.random.default_rng(1)
    A = np.asfortranarray(rng.standard_normal((m, n), dtype=np.float64))
    x = rng.standard_normal(n).astype(np.float64)
    y = rng.standard_normal(m).astype(np.float64)
    alpha, beta = 0.7, -0.2

    @njit(cache=True)
    def gemv(alpha, A, x, beta, y):
        dgemv(np.uint8(ord('N')), m, n, alpha, A, max(1,m), x, 1, beta, y, 1)

    y_ref = alpha * (A @ x) + beta * y
    y2 = y.copy()
    gemv(alpha, A, x, beta, y2)
    assert np.allclose(y2, y_ref, rtol=1e-12, atol=1e-12)

@pytest.mark.parametrize("m,k,n", [(3,4,5), (64,32,16)])
def test_dgemm_NN(m, k, n):
    rng = np.random.default_rng(2)
    A = np.asfortranarray(rng.standard_normal((m, k), dtype=np.float64))
    B = np.asfortranarray(rng.standard_normal((k, n), dtype=np.float64))
    C = np.asfortranarray(rng.standard_normal((m, n), dtype=np.float64))
    alpha, beta = 1.1, -0.3

    @njit(cache=True)
    def gemm(alpha, A, B, beta, C):
        dgemm(np.uint8(ord('N')), np.uint8(ord('N')),
              m, n, k, alpha, A, max(1,m), B, max(1,k), beta, C, max(1,m))

    C_ref = alpha * (A @ B) + beta * C
    C2 = C.copy(order='F')
    gemm(alpha, A, B, beta, C2)
    assert np.allclose(C2, C_ref, rtol=1e-12, atol=1e-12)

@pytest.mark.parametrize("n,nrhs", [(4,1), (32,3)])
def test_dgesv(n, nrhs):
    rng = np.random.default_rng(3)
    A = np.asfortranarray(rng.standard_normal((n, n), dtype=np.float64))
    A += n * np.eye(n, dtype=np.float64)
    B = np.asfortranarray(rng.standard_normal((n, nrhs), dtype=np.float64))

    X_ref = np.linalg.solve(A.copy(order='F'), B.copy(order='F'))

    @njit(cache=True)
    def solve_inplace(A, B, ipiv, info):
        dgesv(n, nrhs, A, max(1,n), ipiv, B, max(1,n), info)

    A_lu = A.copy(order='F')
    B_sol = B.copy(order='F')
    ipiv = np.empty(n, dtype=np.int32, order='F')
    info = np.zeros(1, dtype=np.int32, order='F')
    solve_inplace(A_lu, B_sol, ipiv, info)
    assert info[0] == 0
    assert np.allclose(B_sol, X_ref, rtol=1e-10, atol=1e-10)
