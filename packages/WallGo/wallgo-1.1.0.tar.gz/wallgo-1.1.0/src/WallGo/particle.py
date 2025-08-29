"""
Module with Particle class to hold particle information
"""

import typing
import numpy as np
from .fields import Fields, FieldPoint


class Particle:  # pylint: disable=too-few-public-methods
    """Particle configuration

    A simple class holding attributes of an out-of-equilibrium particle as
    relevant for calculations of Boltzmann equations.
    """

    STATISTICS_OPTIONS: typing.Final[list[str]] = ["Fermion", "Boson"]

    def __init__(
        self,
        name: str,
        index: int,
        msqVacuum: typing.Callable[[Fields | FieldPoint], np.ndarray],
        msqDerivative: typing.Callable[[Fields | FieldPoint], np.ndarray],
        statistics: str,
        totalDOFs: int,
    ) -> None:
        r"""Initialisation

        Parameters
        ----------
        name : string
            A string naming the particle species.
        index : int
            Integer identifier for the particle species. Must be unique
            and match the intended particle index in matrix elements.
        msqVacuum : function
            Function :math:`m^2_0(\phi)`, should take a Fields or FieldPoint object and
            return an array of length Fields.NumPoints(). The background field dependent
            but temperature independent part of the effective mass squared.
        msqDerivative : function
            Function :math:`d(m_0^2)/d(\phi)`, should take a Fields or FieldPoints
            object and return an array of shape Fields.shape.
        statistics : {\"Fermion\", \"Boson\"}
            Particle statistics.
        totalDOFs : int
            Total number of degrees of freedom (should include the multiplicity
            factor).


        Returns
        -------
        cls : Particle
            An object of the Particle class.
        """
        Particle._validateInput(
            name,
            index,
            msqVacuum,
            msqDerivative,
            statistics,
            totalDOFs,
        )
        self.name = name
        self.index = index
        self.msqVacuum = msqVacuum
        self.msqDerivative = msqDerivative
        self.statistics = statistics
        self.totalDOFs = totalDOFs

    @staticmethod
    def _validateInput(  # pylint: disable=unused-argument
        name: str,
        index: int,
        msqVacuum: typing.Callable[[Fields], np.ndarray],
        msqDerivative: typing.Callable[[Fields], np.ndarray],
        statistics: str,
        totalDOFs: int,
    ) -> None:
        """
        Checks that the input fits expectations
        """
        # fields = np.array([1, 1])
        # assert isinstance(msqVacuum(fields), float), \
        #    f"msqVacuum({fields}) must return float"

        if statistics not in Particle.STATISTICS_OPTIONS:
            raise ValueError(f"{statistics=} not in {Particle.STATISTICS_OPTIONS}")
        assert isinstance(totalDOFs, int), "totalDOFs must be an integer"
        assert isinstance(index, int), "index must be an integer"
