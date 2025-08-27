from dataclasses import dataclass


@dataclass
class SolverConfig:
    method: str = "highs"  # scipy.optimize.linprog
    tol: float = 1e-7
    eps: float = 1e-12


DEFAULTS = SolverConfig()
