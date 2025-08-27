import subprocess
import os
import platform
from collections import namedtuple


FlexAIDResult = namedtuple('FlexAIDResult', ['stdout', 'stderr', 'returncode'])

class FlexAIDError(Exception):
    """Custom exception for errors related to the FlexAID."""
    pass


def run_flexaid(config_file_path, ga_file_path, result_save_path, live_output=False):
    """
    Python function to run the FlexAID.

    Args:
        config_file_path: Path to the configuration file (returned by write_config_file()).
        ga_file_path: Path to the GA file (returned by write_ga_file()).
        result_save_path: Path to the folder and name of file without extension where the results will be saved.
        live_output: Prints stdout as it happens to keep track of the progress.
    Returns:
        FlexAIDResult: A namedtuple containing stdout, stderr, and the return code.
    Raises:
        FlexAIDError: If the process fails.
    """

    executable_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'FlexAID')
    if platform.system() == 'Windows':
        executable_path += '.exe'
    if not os.path.isfile(executable_path) or not os.access(executable_path, os.X_OK):
        raise FlexAIDError(f"Executable not found at '{executable_path}'.")
    cmd = [executable_path]

    # Obligatory arguments
    config_file_paths = [config_file_path, ga_file_path]
    for config_file_path in config_file_paths:
        config_file_path = os.path.abspath(config_file_path)
        if not os.path.isfile(config_file_path):
            raise FileNotFoundError(f"Error: File '{config_file_path}' not found.")
        else:
            cmd.extend([config_file_path])
    if not os.path.isdir(os.path.dirname(result_save_path)):
        raise NotADirectoryError(f"Error: The folder in which to write the results: "
                                 f"'{os.path.dirname(result_save_path)}' was not found.")
    cmd.extend([result_save_path])
    if not live_output:
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            return FlexAIDResult(result.stdout, result.stderr, result.returncode)

        except subprocess.CalledProcessError as e:
            error_message = (
                f"FlexAID failed with exit code {e.returncode}.\n"
                f"Stderr:\n{e.stderr.strip()}"
            )
            raise FlexAIDError(error_message) from e

    else:
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
                                       universal_newlines=True)
            stdout_content = []
            stderr_content = []

            print("\n--- Output (stdout) ---")
            for line in iter(process.stdout.readline, ''):
                print(line, end='')
                stdout_content.append(line)

            print("\n--- Errors (stderr) ---")
            for line in iter(process.stderr.readline, ''):
                print(line, end='')
                stderr_content.append(line)

            return_code = process.wait()

            stdout_str = ''.join(stdout_content)
            stderr_str = ''.join(stderr_content)

            if return_code == 0:
                return FlexAIDResult(stdout_str, stderr_str, return_code)
            else:
                print(f"\nFlexAID exited with error code: {return_code}")
                return FlexAIDResult(stdout_str, stderr_str, return_code)

        except Exception as e:
            raise FlexAIDError(f"An unexpected error occurred: {e}")

