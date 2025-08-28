"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2022.
All rights reserved.

Client for the ParityOS cloud services.
"""

import time

from parityos.encodings.parityos_output import ParityOSOutput
from parityos.base.problem_representation import ProblemRepresentation
from parityos.api_interface.exceptions import ParityOSCompilerError, ParityOSTimeoutException
from parityos.api_interface.connection import ClientBase
from parityos.api_interface.compiler_run import CompilerRunStatus, CompilerRun
from parityos.device_model import DeviceModelBase

COMPILE_TIMEOUT = 60 * 15  # seconds
TIME_BETWEEN_TRIALS = 2  # seconds


class CompilerClient(ClientBase):
    """
    Class to be used to make requests to the ParityQC API. It provides methods
    for compiling a ``ProblemRepresentation``, both synchronously and asynchronously,
    and gives access to all the ParityQC API services.
    """

    def compile(
        self,
        optimization_problem: ProblemRepresentation,
        device_model: DeviceModelBase,
        preset: str = None,
        timeout: int = COMPILE_TIMEOUT,
        **kwargs,
    ) -> ParityOSOutput:
        """
        Compiles a logical problem on the given device model. A preset defining the compiler
        options must be given.

        :param optimization_problem: ProblemRepresentation object defining the optimization problem.
        :param device_model: DeviceModel object defining the target device.
        :param preset: the compiler preset to be used.
            ``analog_default`` and ``digital_default`` are available for everyone;
            other allowed presets are communicated on a per-customer basis.
            Optional. If no value is provided, ``device_model.preset`` is used instead.
        :param timeout: time in seconds after which this function is aborted.
        :return: ParityOSOutput object containing all information about the compiled problem
        """
        submission_id = self.submit(optimization_problem, device_model, preset=preset, **kwargs)
        print(f"Compiling submission {submission_id}")

        compiler_runs = []
        stop_time = time.time() + timeout
        while time.time() <= stop_time:
            # Wait for two seconds before contacting the server again.
            time.sleep(TIME_BETWEEN_TRIALS)
            compiler_runs = self.get_compiler_runs(submission_id)

            if compiler_runs and all(
                run.status == CompilerRunStatus.FAILED for run in compiler_runs
            ):
                raise ParityOSCompilerError(
                    f"Compilation failed for submission {submission_id}.\n"
                    + "\n\n".join(str(compiler_run) for compiler_run in compiler_runs)
                )

            completed_runs = [
                run for run in compiler_runs if run.status == CompilerRunStatus.COMPLETED
            ]
            if completed_runs:
                # For now, we only return one solution per compile request
                parityos_output = self.get_solutions(completed_runs[0])[0]
                return parityos_output

        # The compilation did not succeed.
        # We raise an exception, including the information obtained from the server.
        raise ParityOSTimeoutException(
            f"Client-side timeout of {timeout} seconds reached for submission {submission_id}.\n"
            + "\n\n".join(str(compiler_run) for compiler_run in compiler_runs)
        )

    def get_submission(self, submission_id: str) -> dict:
        """
        Returns the submission given a submission id
        """
        response = self._send_request("GET", url=f"{self.base_url}/submissions/{submission_id}")
        return response.json()

    def submit(
        self, optimization_problem: ProblemRepresentation, device_model: DeviceModelBase, **options
    ) -> str:
        """
        Asynchronously submit a problem to the compiler, returns a submission id which can be
        used to request the corresponding compiler runs. The compiler run object can then be used
        to obtain the solutions.

        :param optimization_problem: ProblemRepresentation object defining the optimization problem.
        :param device_model: DeviceModel object defining the target device.
        :param options: options to pass to compilation algorithms.
            For now this is just a single key ``preset`` with value ``analog_default``
            or ``digital_default``. Other presets available upon request.
        :return: id associated with the submission
        """

        url = f"{self.base_url}/submissions"
        optimization_problem_data = optimization_problem.to_json()
        chip_geometry_data = {"device_model": device_model.to_json()}
        # If options contains a preset field equal to None, then change that to device_model.preset.
        preset = options.pop("preset", None) or device_model.preset
        if not options:
            options = {"preset": preset}

        submission_data = {
            "problem": optimization_problem_data,
            "chip_geometry": chip_geometry_data,
            "options": options,
        }
        response = self._send_request("POST", url=url, data=submission_data)
        submission_id = response.json()["submission_id"]
        return submission_id

    def get_solutions(self, compiler_run: CompilerRun) -> list[ParityOSOutput]:
        """
        Get the solutions found by a compiler run.

        :param compiler_run: CompilerRun object
        :return: List of ParityOSOutput objects representing the solutions
        """
        url = f"{self.base_url}/compiler_runs/{compiler_run.id}/solutions"
        response = self._send_request("GET", url=url)
        return [ParityOSOutput.from_json(result["solution"]) for result in response.json()]

    def get_compiler_runs(self, submission_id: str) -> list[CompilerRun]:
        """
        Get the compiler runs spawned by a submission.

        :param submission_id: id of submission
        :return: list of the compiler runs
        """
        url = f"{self.base_url}/submissions/{submission_id}/compiler_runs"
        response = self._send_request("GET", url=url)
        return [CompilerRun.from_json(compiler_run) for compiler_run in response.json()]
