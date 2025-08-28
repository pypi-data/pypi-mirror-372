# ParityOS
Parity Quantum Computing GmbH  
Rennweg 1 Top 314  
6020 Innsbruck, Austria  
Copyright (c) 2020-2023.

This package contains the client software to use the ParityOS cloud service. 

## Installation
It is recommended to install this package in a separate Python `venv` or Conda environment.
```commandline
   # To create a standard Python environment:
   python -m venv my_new_venv  && source my_new_venv/bin/activate
   # Or, alternatively, to create a Anaconda/Miniconda environment:
   conda create --name my_new_conda_env  &&  conda activate my_new_conda_env
```

Installation is done with the following command:
```commandline
pip install parityos
```
This will install two Python libraries: `parityos` and `parityos_addons`.

Some addons depend on external libraries like Cirq, Sympy or Qiskit. 
The `pip` command will resolve these dependencies automatically if you specify which addons you 
want to include. E.g. to include dependencies for the `spin_hamiltonians` and `qiskit_exporter` 
addons, use this command:
```commandline
pip install 'parityos[spinz,qiksit]' 
```
or to use `spin_hamiltonians` and `cirq_exporter`: 
```commandline
pip install 'parityos[spinz,cirq]'
```
These commands will make sure that additional dependencies like `sympy`, `qiskit` or `cirq` 
are installed correctly.
If you want to make sure that all optional dependencies are included, use:
```commandline
pip install 'parityos[all]'
```


## ParityOS
A Python package that provides the `CompilerClient` class to connect to 
the ParityOS cloud service. The package defines data structures to construct
the inputs and to process the outputs from the ParityOS cloud service.

    from parityos import CompilerClient, RectangularDigitalDevice

    username = ''  # Put here your ParityOS username or set the PARITYOS_USER environment variable.
    compiler_client = CompilerClient(username)
    device_model = RectangularDigitalDevice(4, 4)
    parityos_output = compiler_client.compile(hamiltonian, device_model)

## ParityOS Addons
Additional tools that help you to get the most out of the ParityOS framework. 

### addon documentation
Detailed documentation on how to use the ParityOS framework, including a 
quickstart guide and a QAOA tutorial.

To open the documentation in your web browser, type the following command
on the command line:

    python -m parityos_addons.documentation.show

### addon examples
Some examples of ParityOS compilations can be found in `parityos_addons_examples`.
These can be run directly from the command line:

    python -m parityos_addons.examples.example1
    python -m parityos_addons.examples.example2
    python -m parityos_addons.examples.example3
    python -m parityos_addons.examples.example4
    python -m parityos_addons.examples.example5

### addon spin_hamiltonians
A Python package that provides tools to construct a spin Hamiltonian as a product
of Pauli spin Z operators. An example:

    from parityos_addons.spin_hamiltonians import spinz_to_hamiltonian, SpinZ as Z

    hamiltonian = spinz_to_hamiltonian(
        Z('a') + Z('b') - 2 * Z('c') + 4 * Z('a') * Z('b') - (Z('a') + Z('b')) * Z('c')
    ) 

### addon qaoa
A Python package that provides tools to construct a QAOA circuit from the 
output returned by the ParityOS cloud service.

    from parityos_addons.qaoa import generate_qaoa

    parityos_circuit, parameter_bounds = generate_qaoa(parityos_output=parityos_output,
                                                       unitary_pattern='ZCX' * 4)

### addon interfaces
Provides the tools to export quantum circuits from ParityOS to other 
frameworks like Cirq or Qiskit. Here is an example with Qiskit:

    from qiskit.circuit import Parameter
    from parityos_addons.interfaces import QiskitExporter

    # Map ParityOS parameters onto Qiskit parameters
    parameter_map = {key: Parameter(str(key)) for key in parameter_bounds.keys()}
    # Instantiate the exporter
    qiskit_exporter = QiskitExporter(parameter_map=parameter_map, qubit_map=qubit_map)
    # Convert the ParityOS circuit to a qiskit circuit
    qiskit_circuit = qiskit_exporter.to_qiskit(parityos_circuit)

## License
Since version 2.1.0, the ParityOS Client software package is made available 
under the 3-Clause BSD License. See the file `License.txt` for details.
 