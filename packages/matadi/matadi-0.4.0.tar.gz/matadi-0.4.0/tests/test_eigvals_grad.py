import numpy as np

from matadi import Material, MaterialTensor, Variable
from matadi.math import (
    SX,
    cof,
    det,
    eigvals,
    expm,
    inv,
    logm,
    sqrtm,
    sum1,
    trace,
    transpose,
)


def fun(x):
    F = x[0]
    return (sum1(eigvals(transpose(F) @ F))[0, 0] - 3) / 2


def fun_expm(x):
    F = x[0]
    return trace(expm(transpose(F) @ F))[0, 0]


def fun_logm(x):
    F = x[0]
    return trace(logm(transpose(F) @ F))[0, 0]


def fun_sqrtm(x):
    F = x[0]
    return trace(sqrtm(transpose(F) @ F))[0, 0]


def test_eigvals():
    # test several repeated principal stretches
    for w in [1, 1.1, 0.1, 2.4, 12]:
        # variables
        F = Variable("F", 3, 3)

        # data
        np.random.seed(2345537)
        FF = np.random.rand(3, 3, 5, 100)
        for a in range(3):
            FF[a, a] += 1

        # input with repeated equal eigenvalues
        FF[:, :, 0, 1] = np.diag(w * np.ones(3))
        FF[:, :, 0, 2] = np.diag([w, w * 1.01, w])

        # init Material
        W = Material(x=[F], fun=fun)

        WW = W.function([FF])
        dW = W.gradient([FF])
        DW = W.hessian([FF])

        Eye = np.eye(3)
        Eye4 = np.einsum("ij,kl->ikjl", Eye, Eye)

        # check function
        f = FF[:, :, 0, 0]
        c = f.T @ f
        assert np.isclose(WW[0][0, 0, 0, 0], (np.linalg.eigvals(c).sum() - 3) / 2)

        # check gradient
        assert np.allclose(dW[0][:, :, 0, 0], FF[:, :, 0, 0])
        assert np.allclose(dW[0][:, :, 0, 1], FF[:, :, 0, 1])
        assert np.allclose(dW[0][:, :, 0, 2], FF[:, :, 0, 2])

        # check hessian
        assert np.allclose(DW[0][:, :, :, :, 0, 0], Eye4)
        assert np.allclose(DW[0][:, :, :, :, 0, 1], Eye4)
        assert np.allclose(DW[0][:, :, :, :, 0, 2], Eye4)


def test_eigvals_single():
    # variables
    F = Variable("F", 3, 3)

    # data
    FF = np.diag(2.4 * np.ones(3))

    # init Material
    W = Material(x=[F], fun=fun)

    WW = W.function([FF])
    dW = W.gradient([FF])
    DW = W.hessian([FF])

    Eye = np.eye(3)
    Eye4 = np.einsum("ij,kl->ikjl", Eye, Eye)

    # check function
    f = FF
    c = f.T @ f
    assert np.isclose(WW[0], (np.linalg.eigvals(c).sum() - 3) / 2)

    # check gradient
    assert np.allclose(dW[0], FF)

    # check hessian
    assert np.allclose(DW[0], Eye4)


def test_cof():
    # variables
    F = Variable("F", 3, 3)

    # data
    FF = np.diag(2.4 * np.ones(3)).reshape(3, 3, 1, 1)
    dF = np.diag(0.2 * np.ones(3)).reshape(3, 3, 1, 1)

    # fun
    def g(x):
        F = x[0]
        return cof(F)

    # init Material
    W = MaterialTensor(x=[F], fun=g)
    W = MaterialTensor(x=[F], fun=lambda x: x[0])

    Eye = np.eye(3)
    Eye4 = np.einsum("ij,kl->ikjl", Eye, Eye)

    WW = W.gradient([FF])
    dW = W.hessian([FF])

    dW_gvp = W.gradient_vector_product([FF, dF])

    assert np.allclose(np.einsum("ij...,ij...->...", dW[0], dF), dW_gvp)

    assert np.allclose(dW[0][:, :, :, :, 0, 0], Eye4)


def test_mexp():
    # test several repeated principal stretches
    for w in [1, 1.1, 0.1, 2.4, 12]:
        # variables
        F = Variable("F", 3, 3)

        # data
        FF = np.diag([w * 1.01, w, w])
        FF = FF.reshape(3, 3, 1, 1)

        # init Material
        for fun in [fun_expm, fun_logm, fun_sqrtm]:
            W = Material(x=[F], fun=fun)

            WW = W.function([FF])
            dW = W.gradient([FF])
            DW = W.hessian([FF])

            assert not np.any(np.isnan(WW))
            assert not np.any(np.isnan(dW))
            assert not np.any(np.isnan(DW))


if __name__ == "__main__":
    # test several repeated principal stretches
    test_eigvals()
    test_mexp()

    test_eigvals_single()
    test_cof()
