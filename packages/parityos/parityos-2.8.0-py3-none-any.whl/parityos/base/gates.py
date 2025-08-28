"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2024.
All rights reserved.

Classes that store information on quantum gate operations.
"""

from abc import ABC
from collections.abc import Mapping, Sequence, Iterable
from typing import Union

from parityos.base.qubits import Qubit
from parityos.base.utils import json_wrap, JSONType

DEFAULT_PARAMETER_NAME = "parameter"


class Gate(ABC):
    """
    Base class from which all gates inherit.

    The Gate subclasses are intended to store the information received from the compiler.
    They do not implement any methods to simulate the gates, nor do they contain any information
    on the (anti-) commutation relations between them or other mathematical properties.
    For those uses we recommend more elaborate frameworks like Qutip, Cirq or Qiskit.
    """

    gate_map = {}  # a Dict that maps gate names onto gate classes (used by from_json)
    aliases = tuple()  # Alternative names for the class that could appear in JSON representations.

    _gate_map = gate_map  # For backwards compatibility. Will be removed in a future release.

    def __init__(self, *qubit_args: Qubit):
        """
        Set up the list of qubits on which the gate acts.
        """
        self.target_qubits = tuple(qubit_args)

    def __init_subclass__(cls):
        """
        Update the gate map when a new subclass is defined.
        This is used by the `from_json` method to map the JSON data on the correct gate class.
        """
        super().__init_subclass__()
        Gate.gate_map[cls.__name__] = cls
        Gate.gate_map.update({alias: cls for alias in cls.aliases})

    @property
    def qubit_list(self) -> list[Qubit]:
        return list(self.target_qubits)

    @property
    def qubits(self) -> set[Qubit]:
        """
        :return: the set of qubits on which the gate acts (including possible control qubits).
        """
        return set(self.qubit_list)

    @property
    def n_qubits(self):
        return len(self.qubit_list)

    def get_hermitian_conjugate(self) -> "Self":
        """
        :return: the Hermitian conjugate of the gate
        """
        raise NotImplementedError(f"hermitian_conjugate for {type(self)} is not implemented.")

    def make_args(self) -> tuple[Qubit, ...]:
        """
        :return: the sequence of arguments that would be needed to instantiate a copy of self
            (does not include keyword only arguments).
        """
        return self.target_qubits

    @staticmethod
    def make_args_and_kwargs_from_json(data: Sequence[JSONType]) -> tuple[list, dict]:
        """
        :return: the sequence of arguments keyword arguments derived from the given json data
                 that would be needed to create an instance of the class.
        """
        class_name, *gate_data = data
        init_args = [Qubit(label) for label in gate_data]
        init_kwargs = {}
        return init_args, init_kwargs

    def to_json(self) -> list[JSONType]:
        """
        :return: a json compatible object with all the information about the gate.
        """
        return json_wrap([type(self).__name__, *self.make_args()])

    @classmethod
    def from_json(cls, data: Sequence[JSONType]) -> "Self":
        """
        Creates a gate from a json compatible object.

        :param data: gate parameters in json compatible format
        :return: a Gate instance
        """
        # This method redirects the Gate.from_json method to the cls.from_json method,
        # where cls is taken from Gate.gate_map based on the first value in the data.
        gate_class_name, *gate_data = data
        gate_class = cls.gate_map[gate_class_name]
        if cls is Gate:
            # For the abstract class, we delegate to the concrete class.
            return gate_class.from_json(data)
        elif cls is gate_class:
            # Here we define the standard behavior for concrete subclasses.
            # Subclasses can overwrite this if they need more elaborate gate data processing.
            init_args, init_kwargs = cls.make_args_and_kwargs_from_json(data)
            return cls(*init_args, **init_kwargs)
        else:
            raise ValueError(f"Incorrect gate class for {gate_class_name} gate")

    def remap(self, *args, **kwargs) -> "Self":
        """
        The `RMixin.remap` method is used to remap the parameter name of parametrized gates to new
        values. For other gates (the subject of this version), a simple copy of the gate is
        returned.
        """
        # *args and **kwargs are listed (but not consumed) to make sure that the signature is
        # compatible with the signature of RMixin.remap
        return type(self)(*self.make_args())

    def modify_angle(self, *args, **kwargs) -> "Self":
        """
        The `RMixin.modify_angle` method is used to create a new version of the gate, with the same
        arguments except for the angle, which might get a new value.
        For other gates (the subject of this version), a simple copy of the gate is returned.
        """
        # *args and **kwargs are listed (but not consumed) to make sure that the signature is
        # compatible with the signature of RMixin.remap
        return type(self)(*self.make_args())

    def __repr__(self):
        arguments = ", ".join(repr(arg) for arg in self.make_args())
        return f"{type(self).__name__}({arguments})"

    def __eq__(self, other):
        return (type(self) is type(other)) and (self.make_args() == other.make_args())

    def __hash__(self):
        return hash((type(self), self.make_args()))


class Gate1(Gate):
    """
    A Gate that acts on a single qubit.
    """

    def __init__(self, qubit: Qubit):
        """
        :param Qubit qubit: qubit on which the gate acts.
        """
        # We implement __init__ to enforce a single qubit argument
        super().__init__(qubit)

    @property
    def target_qubit(self) -> Qubit:
        """
        Return the qubit on which this gate acts.

        :returns: The qubit on which the gate acts.
        """
        return self.target_qubits[0]


class Gate2(Gate):
    """
    A Gate that acts on two qubits.
    """

    def __init__(self, qubit1: Qubit, qubit2: Qubit):
        """
        :param Qubit qubit1, qubit2: qubits on which the gate acts.
        """
        # We implement __init__ to enforce exactly two qubit arguments
        super().__init__(qubit1, qubit2)


class Gate3(Gate):
    """
    A Gate that acts on three qubits.
    """

    def __init__(self, qubit1: Qubit, qubit2: Qubit, qubit3: Qubit):
        """
        :param Qubit qubit1, qubit2, qubit3: qubits on which the gate acts.
        """
        # We implement __init__ to enforce exactly three qubit arguments
        super().__init__(qubit1, qubit2, qubit3)


class Gate4(Gate):
    """
    A Gate that acts on four qubits.
    """

    def __init__(self, qubit1: Qubit, qubit2: Qubit, qubit3: Qubit, qubit4: Qubit):
        """
        :param Qubit qubit1, qubit2, qubit3, qubit4: qubits on which the gate acts.
        """
        # We implement __init__ to enforce exactly four qubit arguments
        super().__init__(qubit1, qubit2, qubit3, qubit4)


class CMixin(ABC):
    """
    Adds a single control qubit to a gate. This mixin must come before the gate parent class in the
    new class definition.

    Example:
        class CNOT(CMixin, X):  # Creates a class that stores information for a CNOT gate.

    Attributes:
        control_qubits: The tuple of control qubits that can block the operation of the underlying
                        gate.
    """

    def __init__(self, control: Qubit, target: Qubit, *args, **kwargs):
        """
        :param Qubit control: The qubit that controls whether the gate will act
            (if Z_control == -1) or not (if Z_control == 1).
        :param Qubit target: The target qubit on which the controlled operation will act.
                             If the controlled operation acts on more qubits, then these
                             can be provided as additional arguments.
        """
        super().__init__(target, *args, **kwargs)
        self.control_qubits = (control,)

    def make_args(self) -> tuple:
        return *self.control_qubits, *super().make_args()

    @property
    def qubit_list(self) -> list[Qubit]:
        return [*self.control_qubits, *self.target_qubits]


class CCMixin(CMixin, ABC):
    """
    Adds two control qubits to a gate. This mixin must come before the gate parent class in the
    new class definition.

    Example:
        class CCNOT(CCMixin, X):  # Creates a class that stores information for a CCNOT gate.

    Attributes:
        control_qubits: The tuple of control qubits that can block the operation of the underlying
                        gate.
    """

    def __init__(self, control1: Qubit, control2: Qubit, target: Qubit, *args, **kwargs):
        """
        :param Qubit control1:
        :param Qubit control2: The qubits that control whether the gate will act
            (if Z_control1 == Z_control2 == -1) or not (any other Z_control values).
        :param Qubit target: The target qubit on which the controlled operation will act.
                             If the controlled operation acts on more qubits, then these
                             can be provided as additional arguments.
        """
        # We have to call super().__init__ with the correct arguments to make sure that
        # the __init__ methods on all parent classes are consumed in the right order.
        # We skip CMixin.__init__ because that would set the wrong control_qubits attribute.
        super(CMixin, self).__init__(target, *args, **kwargs)
        self.control_qubits = (control1, control2)


class MultiControlMixin(ABC):
    """
    Adds an arbitrary control sequence to a gate. This mixin must come before the gate parent
    class in the new class definition.

    Example:
        class MultiControlledH(MultiControlMixin, H):  # Creates a class that stores information for
        a multi-controlled Hadamard gate.
    """

    def __init__(self, control_qubits: Sequence[Qubit], target: Qubit, *args, **kwargs):
        """
        :param control_qubits: A sequence of control qubits that can block the operation of the
                               underlying gate.
        :param target: The qubit on which the underlying gate should act. If more qubits are
                       targeted, then they can be added as additional arguments.
        """
        super().__init__(target, *args, **kwargs)
        self.control_qubits = tuple(control_qubits)

    @property
    def qubit_list(self) -> list[Qubit]:
        return [*self.control_qubits, *self.target_qubits]

    def make_args(self) -> tuple:
        return self.control_qubits, *super().make_args()

    @classmethod  # Can not be a staticmethod because of `super`.
    def make_args_and_kwargs_from_json(cls, data: Sequence[JSONType]) -> tuple[list, dict]:
        class_name, control_qubits_data, *target_data = data
        control_qubits = [Qubit(label) for label in control_qubits_data]
        super_data = [class_name, *target_data]
        target_args, target_kwargs = super().make_args_and_kwargs_from_json(super_data)
        return [control_qubits, *target_args], target_kwargs


class ConditionalGateMixin(Gate, ABC):
    """
    A mixin that allows the implementation of a gate based on a parity condition.
    """

    def __init__(self, condition: Iterable[Qubit], target_qubits: Iterable[Qubit], **kwargs):
        """
        The *args should be the arguments that are used to construct the class that should be
        executed if the condition evaluates to True.

        The condition is a collection of qubits, from which the most recent measurement results
        determine whether this gate should be executed or not. If the measurement results multiply
        to +1, it will be executed, if the measurement results multiply to -1 it will not be
        executed.

        """
        super().__init__(*target_qubits, **kwargs)
        self.condition = frozenset(condition)

    def make_args(self) -> tuple:
        return *super().make_args(), self.condition

    def to_json(self) -> list[JSONType]:
        args = self.make_args()
        return json_wrap([type(self).__name__, *args])

    @classmethod
    def from_json(cls, data: Sequence[JSONType]) -> "Self":
        *other_data, condition = data
        args_and_kwargs = super().make_args_and_kwargs_from_json(other_data)
        # qubit_args = (Qubit(label) for label in other_data)
        condition = (Qubit(label) for label in condition)
        return cls(condition=condition, target_qubits=args_and_kwargs[0], **args_and_kwargs[1])


class HermitianGateMixin(Gate, ABC):
    """
    A mixin that implements hermitian_conjugate method for Hermitian gates.
    """

    def get_hermitian_conjugate(self) -> "Self":
        """
        :return: the Hermitian conjugate of the gate,
                 which is the copy of itself for Hermitian gates
        """
        return type(self)(*self.make_args())


class RMixin(Gate, ABC):
    """
    A mixin that converts a gate into a rotated gate.

    Attributes:
        angle: the angle for the gate rotation
        parameter_name: a label that identifies the parameter with which to multiply
        the angle when implementing it. If no parameter name is given, then the gate is
        considered to be a 'Fixed' gate. If a parameter name is given, then the gate is
        considered to be a 'Parametrized' gate. This is reflected in the name of the gate
        in the output generated by the `to_json` method.
    """

    _FIXED = "Fixed"
    _PARAMETRIZED = "Parametrized"
    _DEFAULT_PARAMETER_NAME = DEFAULT_PARAMETER_NAME

    def __init_subclass__(cls):
        """
        Update the gate map with the class name + suffixes when a new subclass is defined.
        """
        cls.aliases = f"{cls.__name__}{cls._FIXED}", f"{cls.__name__}{cls._PARAMETRIZED}"
        super().__init_subclass__()

    def __init__(self, *args: Union[Qubit, float], parameter_name: str = None, **kwargs):
        """
        :param Qubit args: a list of Qubits on which the gate acts
        :param float angle: the angle for the gate rotation
        :param str parameter_name: a label that identifies the parameter with which to multiply
                                   the angle when implementing it.
        """
        # angle is a mandatory argument, but it should be given after the qubit args.
        if "angle" in kwargs:
            super_args = args
            angle = kwargs.pop("angle")
        else:
            *super_args, angle = args

        super().__init__(*super_args, **kwargs)
        self.angle = angle
        self.parameter_name = parameter_name

    @property
    def parameters(self) -> set[str]:
        """
        :return: the set of parameters (strings)
        """
        return {self.parameter_name} if self.parameter_name else set()

    def get_hermitian_conjugate(self) -> "Self":
        """
        :return: the Hermitian conjugate of the gate
        """
        *init_args, angle = self.make_args()
        return type(self)(*init_args, -angle, parameter_name=self.parameter_name)

    def remap(self, context: Mapping = None, **kwargs) -> Gate:
        """
        Creates a copy of the gate with an updated parameter or parameter name.

        Updates for the parameter should be provided either as a context mapping or as a keyword
        argument. If a keyword argument is given, its key must match the parameter_name defined
        on the gate, otherwise an error will be raised.
        If no keyword argument is given, then the parameter_name is looked up in the context. If it
        is found, then the parameter is remapped to the corresponding value. Otherwise, a copy of
        the gate is returned.

        If the provided value is a string, then it is interpreted as a new parameter name and the
        resulting gate is again a parametrized gate.
        Otherwise, the value should be a number-like object (an int, a float, a numpy float or even
        a Sympy symbol or a Qiskit Parameter can be used). Then the returned gate is a fixed gate
        where the angle has been multiplied with the number-like object.

        A keyword argument takes precedence over the context argument.

        :param context: a mapping of parameter names (strings) to parameter values (number-like
                        objects) or to new parameter names (strings).


        Examples:
            rz_gate = RZ(Qubit(1), angle=math.pi, parameter_name='parameter')
            # Create a copy of rz_gate where the parameter_name is changed to 'theta'.
            rz_theta = rz_gate.remap(parameter='theta')
            rz_theta = rz_gate.remap({'parameter': 'theta', 'other_parameter': 'gamma'})

            # Convert rz_theta into a fixed gate with the angle divided by two:
            rz_fixed = rz_theta.remap(theta=0.5)
            rz_fixed = rz_theta.remap({'theta': 0.5, 'gamma': 2.5})
        """
        if context is None:
            context = {}

        if self.parameter_name is None:
            # For a fixed gate, simply return a copy of the original gate.
            return super().remap(context=context, **kwargs)

        value = (
            kwargs[self.parameter_name]
            if kwargs
            else context.get(self.parameter_name, self.parameter_name)
        )
        # The second argument self.parameter_name makes sure that we create a copy of the
        # original gate if self.parameter_name was not included in the context.

        cls = type(self)
        copy_args = self.make_args()
        if isinstance(value, str):
            # A string value means redefining the parameter_name.
            return cls(*copy_args, parameter_name=value)
        else:
            # Otherwise, value is a number-like object with which to multiply the angle.
            *gate_args, angle = copy_args
            return cls(*gate_args, angle * value)

    def modify_angle(
        self,
        angle_map: Mapping[frozenset[Qubit], float],
        gate_type: type[Gate] = None,
        parameter_name: str = None,
    ) -> Gate:
        """
        Create a new gate with the same arguments as this one, except for rotation gates of the
        given gate type and with the given parameter_name as parameter,
        for which the angle will be changed to the value given by the angle map, in function
        of the qubit(s) on which the gate acts. If the qubit(s) are not included in the angle map,
        then the angle is left unchanged.

        If the gate type is not specified, then all rotation gates might be affected. If the
        parameter name is not specified, then also gates without parameters might be affected.

        :param angle_map: A mapping that provides a new angle for each of the qubit sets on which
                          the gates might act.
        :param gate_type: Optional. If given, then only gates of this type will be updated. Other
                          gates will be copied into the new circuit without changes. Default is
                          None.
        :param parameter_name: Optional. If given, then only gates with this parameter name will be
                               updated. Other gates will be copied into the new circuit without
                               changes. Default is None.

        :returns: A new circuit with all the gates copied over from the current circuit, except for
                  selected rotation gates for which the rotation angle will have been modified.
                  Default is None.

        """
        *qubits, angle = self.make_args()
        if ((gate_type is None) or isinstance(self, gate_type)) and (
            (parameter_name is None) or (self.parameter_name == parameter_name)
        ):
            # If the qubits are not present in angle_map, then we keep the current angle.
            angle = angle_map.get(frozenset(qubits), angle)

        return type(self)(*qubits, angle, parameter_name=self.parameter_name)

    def make_args(self) -> tuple:
        """
        :return: the sequence of arguments that would be needed to instantiate a copy of self.
        """
        # Note that instantiating a copy of self also requires the keyword argument 'parameter'
        # if parameter is not None.
        args = super().make_args()
        return *args, self.angle

    def to_json(self) -> list[JSONType]:
        """
        :return: a json compatible object with all the information about the gate.
        """
        args = self.make_args()
        if self.parameter_name is None:
            return json_wrap([type(self).__name__ + self._FIXED, *args])
        elif self.parameter_name == self._DEFAULT_PARAMETER_NAME:
            return json_wrap([type(self).__name__ + self._PARAMETRIZED, *args])
        else:
            # For gates with a non-standard parameter value we should include the parameter.
            return json_wrap([type(self).__name__, *args, self.parameter_name])

    @classmethod
    def make_args_and_kwargs_from_json(cls, data: Sequence[JSONType]) -> tuple[list, dict]:
        class_name, *gate_data = data
        if isinstance(gate_data[-1], str):
            *data, parameter_name = data
        elif class_name.endswith(cls._PARAMETRIZED):
            parameter_name = cls._DEFAULT_PARAMETER_NAME
        else:
            parameter_name = None

        *super_data, angle = data
        init_args, init_kwargs = super().make_args_and_kwargs_from_json(super_data)
        init_kwargs.update(angle=angle, parameter_name=parameter_name)
        return init_args, init_kwargs

    def __repr__(self):
        arguments = ", ".join(repr(arg) for arg in self.make_args())
        if self.parameter_name is not None:
            arguments += f", parameter_name='{self.parameter_name}'"

        return f"{type(self).__name__}({arguments})"

    def __eq__(self, other):
        return super().__eq__(other) and (self.parameter_name == other.parameter_name)

    def __hash__(self):
        # Since we redefine __eq__, we should also explicitly redirect __hash__ to super(),
        # otherwise it will return None.
        # https://docs.python.org/3.9/reference/datamodel.html#object.__hash__
        return super().__hash__()


####################################################################################################


class X(HermitianGateMixin, Gate1):
    """Represents an X gate"""


class SX(Gate1):
    """Represents a square root X gate"""


class Y(HermitianGateMixin, Gate1):
    """Represents a Y gate"""


class Z(HermitianGateMixin, Gate1):
    """Represents a Z gate"""


class H(HermitianGateMixin, Gate1):
    """Represents a Hadamard gate"""


class Swap(Gate2):
    """Represents a Swap gate"""


class ISwap(Gate2):
    """Represents an iSwap gate"""


class CH(CMixin, H):
    """Represents a CH gate"""


class CNOT(CMixin, X):
    """Represents a CNOT gate"""

    aliases = ("CX",)


class CY(CMixin, Y):
    """Represents a CY gate"""


class CZ(CMixin, Z):
    """Represents a CZ gate"""


class CP(CMixin, RMixin, Gate1):
    """Represents a Controled Phase gate"""


class Rx(RMixin, Gate1):
    """Represents an RX gate"""


class Ry(RMixin, Gate1):
    """Represents an RY gate"""


class Rz(RMixin, Gate1):
    """Represents an RZ gate"""


class Rxx(RMixin, Gate2):
    """Represents an RXX gate"""


class Ryy(RMixin, Gate2):
    """Represents an RYY gate"""


class Rzz(RMixin, Gate2):
    """Represents an RZZ gate"""


class Rzzzz(RMixin, Gate4):
    """Represents an RZZZZ gate"""


class CRx(CMixin, Rx):
    """Represents a controlled Rx gate"""


class CRy(CMixin, Ry):
    """Represents a controlled Ry gate"""


class CRz(CMixin, Rz):
    """Represents a controlled Rz gate"""


class CCNOT(CCMixin, X):
    """Represents a CCNOT gate"""

    aliases = ("CCX",)


class CCZ(CCMixin, Z):
    """Represents a CCZ gate"""


class MultiControlledRx(MultiControlMixin, Rx):
    """Represents a controlled Rx gate with arbitrary control sequence"""


class MultiControlledRy(MultiControlMixin, Ry):
    """Represents a controlled Ry gate with arbitrary control sequence"""


class MultiControlledRz(MultiControlMixin, Rz):
    """Represents a controlled Rz gate with arbitrary control sequence"""


class MultiControlledH(MultiControlMixin, H):
    """Represents a controlled Hadamard gate with arbitrary control sequence"""


class MeasureZ(Gate1):
    """
    A measurement of a qubit in the Z basis
    """


class ConditionalX(ConditionalGateMixin, X):
    """
    An X gate that is only executed based on a certain parity condition
    """


class ConditionalZ(ConditionalGateMixin, Z):
    """
    An X gate that is only executed based on a certain parity condition
    """


class ConditionalRx(ConditionalGateMixin, Rx):
    """
    An Rx gate that is only executed based on a certain parity condition
    """
