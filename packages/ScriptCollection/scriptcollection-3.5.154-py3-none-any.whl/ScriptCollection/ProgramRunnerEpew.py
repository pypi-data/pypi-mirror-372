import os
import base64
import tempfile
from subprocess import Popen
from uuid import uuid4

from .GeneralUtilities import GeneralUtilities
from .ProgramRunnerBase import ProgramRunnerBase
from .ProgramRunnerPopen import ProgramRunnerPopen


class CustomEpewArgument:

    print_errors_as_information: bool
    log_file: str
    timeoutInSeconds: int
    addLogOverhead: bool
    title: str
    log_namespace: str
    verbosity: int
    arguments_for_log:  list[str]
    tempdir = os.path.join(tempfile.gettempdir(), str(uuid4()))
    stdoutfile = tempdir + ".epew.stdout.txt"
    stderrfile = tempdir + ".epew.stderr.txt"
    exitcodefile = tempdir + ".epew.exitcode.txt"
    pidfile = tempdir + ".epew.pid.txt"

    def __init__(self, print_errors_as_information: bool, log_file: str, timeoutInSeconds: int, addLogOverhead: bool, title: str, log_namespace: str, verbosity: int,  arguments_for_log:  list[str]):
        self.print_errors_as_information = print_errors_as_information
        self.log_file = log_file
        self.timeoutInSeconds = timeoutInSeconds
        self.addLogOverhead = addLogOverhead
        self.title = title
        self.log_namespace = log_namespace
        self.verbosity = verbosity
        self.arguments_for_log = arguments_for_log


class ProgramRunnerEpew(ProgramRunnerBase):

    @GeneralUtilities.check_arguments
    def run_program_argsasarray_async_helper(self, program: str, arguments_as_array: list[str] = [], working_directory: str = None, custom_argument: object = None, interactive: bool = False) -> Popen:
        if GeneralUtilities.epew_is_available():
            custom_argument: CustomEpewArgument = custom_argument
            args = []

            base64argument = base64.b64encode(' '.join(arguments_as_array).encode('utf-8')).decode('utf-8')
            args.append(f'-p "{program}"')
            args.append(f'-a {base64argument}')
            args.append('-b')
            args.append(f'-w "{working_directory}"')
            if custom_argument.stdoutfile is not None:
                args.append(f'-o {custom_argument.stdoutfile}')
            if custom_argument.stderrfile is not None:
                args.append(f'-e {custom_argument.stderrfile}')
            if custom_argument.exitcodefile is not None:
                args.append(f'-x {custom_argument.exitcodefile}')
            if custom_argument.pidfile is not None:
                args.append(f'-r {custom_argument.pidfile}')
            args.append(f'-d {str(custom_argument.timeoutInSeconds*1000)}')
            args.append(f'-t "{custom_argument.title}"')
            args.append(f'-l "{custom_argument.log_namespace}"')
            if not GeneralUtilities.string_is_none_or_whitespace(custom_argument.log_file):
                args.append(f'-f "{custom_argument.log_file}"')
            if custom_argument.print_errors_as_information:
                args.append("-i")
            if custom_argument.addLogOverhead:
                args.append("-g")
            args.append("-v "+str(custom_argument.verbosity))
            return ProgramRunnerPopen().run_program_argsasarray_async_helper("epew", args, working_directory, custom_argument, interactive)
        else:
            raise ValueError("Epew is not available.")

    # Return-values program_runner: Exitcode, StdOut, StdErr, Pid
    @GeneralUtilities.check_arguments
    def wait(self, process: Popen, custom_argument: object = None) -> tuple[int, str, str, int]:
        process.wait()
        custom_argument: CustomEpewArgument = custom_argument
        stdout = self.__load_text(custom_argument.output_file_for_stdout)
        stderr = self.__load_text(custom_argument.output_file_for_stderr)
        exit_code = self.__get_number_from_filecontent(self.__load_text(custom_argument.output_file_for_exit_code))
        pid = self.__get_number_from_filecontent(self.__load_text(custom_argument.output_file_for_pid))
        GeneralUtilities.ensure_directory_does_not_exist(custom_argument.tempdir)
        result = (exit_code, stdout, stderr, pid)
        return result

    @GeneralUtilities.check_arguments
    def run_program_argsasarray(self, program: str, arguments_as_array: list[str] = [], working_directory: str = None, custom_argument: object = None, interactive: bool = False) -> tuple[int, str, str, int]:
        process: Popen = self.run_program_argsasarray_async_helper(program, arguments_as_array, working_directory, custom_argument, interactive)
        return self.wait(process, custom_argument)

    @GeneralUtilities.check_arguments
    def run_program(self, program: str, arguments: str = "", working_directory: str = None, custom_argument: object = None, interactive: bool = False) -> tuple[int, str, str, int]:
        return self.run_program_argsasarray(program, GeneralUtilities.arguments_to_array(arguments), working_directory, custom_argument, interactive)

    @GeneralUtilities.check_arguments
    def run_program_argsasarray_async(self, program: str, arguments_as_array: list[str] = [], working_directory: str = None, custom_argument: object = None, interactive: bool = False) -> int:
        return self.run_program_argsasarray_async_helper(program, arguments_as_array, working_directory, custom_argument, interactive).pid

    @GeneralUtilities.check_arguments
    def run_program_async(self, program: str, arguments: str = "", working_directory: str = None, custom_argument: object = None, interactive: bool = False) -> int:
        return self.run_program_argsasarray_async(program, GeneralUtilities.arguments_to_array(arguments), working_directory, custom_argument, interactive)

    @GeneralUtilities.check_arguments
    def __get_number_from_filecontent(self, filecontent: str) -> int:
        for line in filecontent.splitlines():
            try:
                striped_line = GeneralUtilities.strip_new_line_character(line)
                result = int(striped_line)
                return result
            except:
                pass
        raise ValueError(f"'{filecontent}' does not containe an int-line")

    @GeneralUtilities.check_arguments
    def __load_text(self, file: str) -> str:
        if os.path.isfile(file):
            content = GeneralUtilities.read_text_from_file(file).replace('\r', '')
            os.remove(file)
            return content
        else:
            raise ValueError(f"File '{file}' does not exist")

    @GeneralUtilities.check_arguments
    def will_be_executed_locally(self) -> bool:
        return True
