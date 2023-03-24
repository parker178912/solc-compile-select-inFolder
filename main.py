import argparse
import subprocess
import sys
from multiprocessing import Pool
from glob import glob
from dataclasses import dataclass
from solc_select.solc_select import (
    installed_versions,
    install_artifacts,
    halt_old_architecture,
)  # ,switch_global_version
from solc_select.constants import ARTIFACTS_DIR
from versionchecker import VersionChecker


@dataclass
class CompiledData:
    """
    A dataclass which contain 4 properties : Opcodes, ByteCode, RuntimeCode, Version
    """

    Opcodes: str = None
    ByteCode: str = None
    RuntimeCode: str = None
    Compile_version: str = None


def compile(file: str, version: str) -> CompiledData:
    """
    Compile file with the version of solc-bin.

    ### Args :
        file : the file path you want to compile.
        version : the version of solc-bin you want to use.

    ### Returns :
        data : CompilesData dataclass after compiled.

    """
    # switch_global_version(version, True)
    # -> Because we use path to execute solc-bin, so we don't need to switch global version.
    if version not in installed_versions():
        install_artifacts(version)
    path = ARTIFACTS_DIR.joinpath(f"solc-{version}", f"solc-{version}")
    halt_old_architecture(path)
    sys.argv = [file, "--opcodes", "--bin", "--bin-runtime"]
    try:
        print("Compile version : ", version)
        res = subprocess.check_output(
            [str(path)] + sys.argv,
        )
        result = res.decode("utf-8").split("\n")
        data = CompiledData(
            Opcodes=result[3], ByteCode=result[5], RuntimeCode=result[7], Compile_version=version
        )
    except subprocess.CalledProcessError as e:
        data = None
        print(
            "There're something wrong in your solidity code when compiling, please check the upper wrong message."
        )
    return data


def version_decide(file: str) -> CompiledData:
    """
    Decide version by calling versionchecker.py and call compile function to do compile.

    ### Args :
        file : the file name you want to compile.

    ### Output :
        data : CompilesData dataclass after compiled.

    """
    checkversion = VersionChecker(file)
    _ = checkversion.resolve_pragma()
    _ = checkversion.get_all_version_data()
    print("Solidity file: ", checkversion.sol_file)
    print("Pragma : ", checkversion.pragma)
    print("    - Available versions", checkversion.available_versions)
    print("    - Lowest version", checkversion.lowest_version)
    print("    - Latest version", checkversion.latest_version)
    if len(checkversion.available_versions) != 0:
        data = compile(checkversion.sol_file, checkversion.lowest_version)
        print(data)
    else:
        print("You don't have available versions, please check your pragma.")


if __name__ == "__main__":
    """
    Main program to set multiprocessing and call version_decide function to do compile.

    ### Args :
        path : the folder path which you want to compile inside solidity file.

    """
    parser = argparse.ArgumentParser(
        description="Compile a Solidity file with a specific version of solc."
    )
    parser.add_argument("path", help="The Solidity folder path to compile")

    args = parser.parse_args()
    filelists = glob(f"{args.path}/*.sol")
    process_pool = Pool(processes=4)

    process_pool.map(version_decide, filelists)

    process_pool.close()
    process_pool.join()
