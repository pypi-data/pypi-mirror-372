"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023-2025.
All rights reserved.
"""

from dataclasses import dataclass, asdict

from parityos.base.utils import JSONType


@dataclass(frozen=True)
class Detuning:
    """
    Represents the detuning for a single atom, consisting of the problem detuning J,
    alpha, and compensation, c.f. [Lanthaler et.al., Phys. Rev. Lett. 130, 220601 (2023)].

    :param J: Problem specific detuning (rad/μs).
    :param alpha: Base detuning (rad/μs).
    :param compensation: Compensation for the vdW interaction tails (rad/μs).
    """

    J: float = 0.0
    alpha: float = 0.0
    compensation: float = 0.0

    @property
    def value(self) -> float:
        return self.J + self.alpha + self.compensation

    def to_json(self) -> JSONType:
        return asdict(self)

    @classmethod
    def from_json(cls, data: JSONType) -> "Detuning":
        return cls(**data)
