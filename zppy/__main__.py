import argparse
import errno
import os

from configobj import ConfigObj
from validate import Validator

from zppy.amwg import amwg
from zppy.climo import climo
from zppy.e3sm_diags import e3sm_diags
from zppy.e3sm_diags_vs_model import e3sm_diags_vs_model
from zppy.global_time_series import global_time_series
from zppy.mpas_analysis import mpas_analysis
from zppy.ts import ts


def main():

    # Command line parser
    parser = argparse.ArgumentParser(
        description="Launch E3SM post-processing tasks", usage="zppy -c <config>"
    )
    parser.add_argument(
        "-c", "--config", type=str, help="configuration file", required=True
    )
    args = parser.parse_args()

    # Subdirectory where templates are located
    templateDir = os.path.join(os.path.dirname(__file__), "templates")

    # Read configuration file and validate it
    config = ConfigObj(args.config, configspec=os.path.join(templateDir, "default.ini"))
    validator = Validator()

    result = config.validate(validator)
    if result is not True:
        print("Validation results={}".format(result))
        raise Exception("Configuration file validation failed")
    else:
        print("Configuration file validation passed")

    # Add templateDir to config
    config["default"]["templateDir"] = templateDir

    # Output script directory
    output = config["default"]["output"]
    scriptDir = os.path.join(output, "post/scripts")
    try:
        os.makedirs(scriptDir)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            print("Cannot create script directory")
            raise Exception
        pass

    if "environment_commands" not in config["default"].keys():
        if "E3SMU_SCRIPT" in os.environ:
            environment_commands = "source {}".format(os.environ["E3SMU_SCRIPT"])
        else:
            if "CONDA_EXE" not in os.environ or "CONDA_DEFAULT_ENV" not in os.environ:
                raise ValueError(
                    "zppy does not seem to be running in a conda environment. "
                    "Cannot determine environment to activate in job scripts. "
                    "Please set environment_commands config option."
                )
            base_path = os.path.dirname(os.path.dirname(os.environ["CONDA_EXE"]))
            environment_commands = (
                "source {}/etc/profile.d/conda.sh\nconda activate {}".format(
                    base_path, os.environ["CONDA_DEFAULT_ENV"]
                )
            )

        config["default"]["environment_commands"] = environment_commands

    # Determine machine to decide which header files to use
    hostname = os.getenv("HOSTNAME")
    if hostname is None:
        raise ValueError(
            "Could not determine the hostname used to identify this machine."
        )

    if hostname.startswith("compy"):
        machine = "compy"
    elif hostname.startswith("cori"):
        machine = "cori"
    elif hostname.startswith("blues"):
        machine = "anvil"
    elif hostname.startswith("chr"):
        machine = "chrysalis"
    else:
        raise ValueError("Hostname {} is not a machine known to zppy.".format(hostname))
    config["default"]["machine"] = machine

    # climo tasks
    climo(config, scriptDir)

    # time series tasks
    ts(config, scriptDir)

    # e3sm_diags tasks
    e3sm_diags(config, scriptDir)

    # e3sm_diags_vs_model tasks
    e3sm_diags_vs_model(config, scriptDir)

    # amwg tasks
    amwg(config, scriptDir)

    # mpas_analysis tasks
    mpas_analysis(config, scriptDir)

    # global time series tasks
    global_time_series(config, scriptDir)
