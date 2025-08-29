from .._templates import MaterialTensorGeneral
from ..math import gradient
from ._hyperelasticity_isotropic import neo_hooke
from ._misc import morph
from ._pseudo_elasticity import ogden_roxburgh
from ._viscoelasticity import finite_strain_viscoelastic, finite_strain_viscoelastic_mr


class NeoHookeOgdenRoxburgh(MaterialTensorGeneral):
    "Neo-Hooke and Ogden-Roxburgh material formulation."

    def __init__(self, C10=0.5, r=3, m=1, beta=0):
        def fun(x, C10, r, m, beta):
            # split `x` into the deformation gradient and the state variable
            F, Wmaxn = x[0], x[-1]

            # isochoric and volumetric parts of the hyperelastic
            # strain energy function
            W = neo_hooke(F, C10)

            # pseudo-elastic softening function
            eta, Wmax = ogden_roxburgh(W, Wmaxn, r, m, beta)

            # first Piola-Kirchhoff stress and updated state variable
            # for a pseudo-elastic material formulation
            return eta * gradient(W, F), Wmax

        super().__init__(fun=fun, statevars_shape=(1, 1), C10=C10, r=r, m=m, beta=beta)


class Morph(MaterialTensorGeneral):
    "MORPH consitutive material formulation."

    def __init__(
        self,
        p1=0.035,
        p2=0.37,
        p3=0.17,
        p4=2.4,
        p5=0.01,
        p6=6.4,
        p7=5.5,
        p8=0.24,
    ):
        def fun(x, p1, p2, p3, p4, p5, p6, p7, p8):
            P, statevars = morph(x, p1, p2, p3, p4, p5, p6, p7, p8)

            return P, statevars

        super().__init__(
            fun=fun,
            statevars_shape=(13, 1),
            p1=p1,
            p2=p2,
            p3=p3,
            p4=p4,
            p5=p5,
            p6=p6,
            p7=p7,
            p8=p8,
        )


class Viscoelastic(MaterialTensorGeneral):
    "Finite strain viscoelastic material formulation."

    def __init__(
        self,
        mu=1,
        eta=1,
        dtime=1,
    ):
        def fun(x, mu, eta, dtime):
            P, statevars = finite_strain_viscoelastic(x, mu, eta, dtime)
            return P, statevars

        super().__init__(
            fun=fun,
            statevars_shape=(6, 1),
            mu=mu,
            eta=eta,
            dtime=dtime,
        )


class ViscoelasticMooneyRivlin(MaterialTensorGeneral):
    "Finite strain viscoelastic material formulation with Mooney-Rivlin hyperelasticity."

    def __init__(
        self,
        c10=1,
        c01=1,
        eta=1,
        dtime=1,
    ):
        def fun(x, c10, c01, eta, dtime):
            P, statevars = finite_strain_viscoelastic_mr(x, c10, c01, eta, dtime)
            return P, statevars

        super().__init__(
            fun=fun,
            statevars_shape=(6, 1),
            c10=c10,
            c01=c01,
            eta=eta,
            dtime=dtime,
        )
