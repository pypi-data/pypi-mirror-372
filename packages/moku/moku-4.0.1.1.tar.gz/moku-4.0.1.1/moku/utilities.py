import json
import os
from pathlib import Path
import platform
from subprocess import PIPE, Popen

from packaging.specifiers import SpecifierSet

from .exceptions import InvalidParameterRange, MokuException, MokuNotFound, NoInstrumentBitstream
from .finder import Finder
from .version import COMPAT_MOKUCLI

from .logging import get_logger
logger = get_logger(__name__.split('.')[-1])

def find_moku_by_serial(serial):
    result = Finder().find_all(timeout=10, filter=lambda x: x.serial == serial)
    if len(result) > 0:
        return result[0].ipv4_addr
    raise MokuNotFound()


def check_mokucli_version(cli_path):
    req_ver = SpecifierSet(COMPAT_MOKUCLI)
    out, _ = Popen([cli_path, "--version"], stdout=PIPE, stderr=PIPE).communicate()
    if not out:
        raise MokuException(
            f"Cannot find mokucli. \n"
            "Please download latest version of the CLI from https://www.liquidinstruments.com/software/utilities/. \n"  # noqa
            "If you have already installed, please set the MOKU_CLI_PATH environment variable to absolute path of mokucli."
        )

    ver_str = out.decode("utf8").rstrip()
    if not req_ver.contains(ver_str):
        raise InvalidParameterRange(
            f"mokucli version {ver_str} is not compatible with this version of the API. \n"
            f"The minimum required version is {req_ver}. \n"
            "Please download latest version of the CLI from https://www.liquidinstruments.com/software/utilities/. \n"  # noqa
            "If you have already installed, please set the MOKU_CLI_PATH environment variable to absolute path of mokucli."
        )

def get_config_dir() -> Path:
    """Get the platform-specific configuration directory.

    This path resolution should exactly match the logic in mokucli.

    Corrolary: If you change this, change it in mokucli as well.
    """
    if platform.system() == "Windows":
        # If APPDATA is not set, use the user's home directory
        return Path(os.environ.get("APPDATA", Path.home())) / "Moku"
    elif platform.system() == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Moku"
    else:  # Linux and others
        return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "moku"

def get_version_info(mokuOS_version):
    version_file = get_config_dir() / "data" / "versions" / f"{mokuOS_version}.json"
    logger.debug(f"Looking for version info in {version_file}")
    if not version_file.exists():
        raise NoInstrumentBitstream()
    with open(version_file, "r") as f:
        return json.load(f)

def get_bitstream_path(mokuOS_version, hardware):
    hw_dir = {"mokupro": "mokupro", "mokugo": "mokugo", "mokulab": "moku20", "mokudelta": "mokuaf"}
    version_info = get_version_info(mokuOS_version)
    bitstream_path = get_config_dir() / "data" / "instruments" / version_info["instruments"] / hw_dir[hardware]
    logger.debug(f"Bitstream path: {bitstream_path}")
    if not bitstream_path.exists():
        raise NoInstrumentBitstream()
    return bitstream_path
