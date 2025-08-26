import json
import pathlib
import subprocess
import tarfile
from os import environ
from pathlib import Path
from shutil import which
import warnings

from moku.exceptions import (IncompatibleMokuException,
                             IncompatiblePackageException, MokuException, MokuNotFound,
                             NoInstrumentBitstream)
from moku.session import RequestSession
from moku.version import COMPAT_MOKUOS, SUPPORTED_PROXY_VERSION
from requests.exceptions import ConnectionError

from .utilities import check_mokucli_version, get_bitstream_path, get_config_dir
from .logging import get_logger

# Set up logger for this module
logger = get_logger(__name__.split('.')[-1])

# Look for mokucli in the path or in the MOKU_CLI_PATH environment variable
if MOKU_CLI_PATH := environ.get("MOKU_CLI_PATH", which("mokucli")):
    MOKU_CLI_PATH = str(Path(MOKU_CLI_PATH).expanduser())
else:
    warnings.warn("Can't find mokucli, which is required for correct operation. Please install from https://liquidinstruments.com/software/utilities/ or set the MOKU_CLI_PATH environment variable to the path of the mokucli executable. Using default path.")

# The MOKU_DATA_PATH environment variable is used to override the default data path,
# which is picked up from the mokucli or by using the same logic as mokucli
# which we reproduce in the utilities.py module.
if MOKU_DATA_PATH := environ.get("MOKU_DATA_PATH"):
    MOKU_DATA_PATH = Path(MOKU_DATA_PATH).expanduser()
else:
    if MOKU_CLI_PATH:
        _data_path = subprocess.check_output([MOKU_CLI_PATH, "config", "which"]).decode("utf-8").strip()
        MOKU_DATA_PATH = Path(_data_path).parent.joinpath("data")
    else:
        MOKU_DATA_PATH = get_config_dir().joinpath("data")

class MultiInstrumentSlottable:
    """Mixin to handle common instrument initialization pattern for multi-instrument capable devices.

    Must mix in to a class that also extends Moku in order to get bitstream upload implementation.
    """

    # Subclasses must define these
    INSTRUMENT_ID = None
    OPERATION_GROUP = None

    def _init_instrument(self, ip=None, serial=None, force_connect=False,
                        ignore_busy=False, persist_state=False,
                        connect_timeout=15, read_timeout=30,
                        slot=None, multi_instrument=None, bs_path=None, **kwargs):
        """Common initialization logic for all instruments.

        Args:
            bs_path: Optional path to custom bitstream file. If provided, this will be
                    used instead of the standard instrument bitstream.
        """

        if self.INSTRUMENT_ID is None or self.OPERATION_GROUP is None:
            raise NotImplementedError("Subclass must define INSTRUMENT_ID and OPERATION_GROUP")

        # Get instrument-specific logger
        self._logger = get_logger(f'instruments.{self.__class__.__name__}')
        self._logger.debug(f"Initializing {self.__class__.__name__} (ID={self.INSTRUMENT_ID})")

        self.id = self.INSTRUMENT_ID
        self.operation_group = self.OPERATION_GROUP

        if multi_instrument is None:
            # Standalone mode
            self.slot = 1
            self._logger.debug("Initializing in standalone mode (slot=1)")
            if not any([ip, serial]):
                raise MokuException("IP (or) Serial is required")
            if serial:
                from moku.utilities import find_moku_by_serial
                self._logger.debug(f"Finding Moku by serial: {serial}")
                ip = find_moku_by_serial(serial)

            # Call Moku.__init__
            super().__init__(
                ip=ip,
                force_connect=force_connect,
                ignore_busy=ignore_busy,
                persist_state=persist_state,
                connect_timeout=connect_timeout,
                read_timeout=read_timeout,
                **kwargs,
            )
            self.upload_bitstream("01-000")
            self.upload_bitstream(f"01-{self.id:03}-00", bs_path=bs_path)
        else:
            # Multi-instrument mode
            self.platform_id = multi_instrument.platform_id
            self.slot = slot
            self.session = multi_instrument.session
            self.mokuOS_version = multi_instrument.mokuOS_version
            self.hardware = multi_instrument.hardware
            self.bitstreams = multi_instrument.bitstreams
            self.manage_bitstreams = multi_instrument.manage_bitstreams
            self._logger.info(f"Uploading bitstream for {self.__class__.__name__} in slot {self.slot}")
            self.upload_bitstream(
                f"{self.platform_id:02}-{self.id:03}-{self.slot - 1:02}",
                bs_path=bs_path
            )
            self._logger.debug(f"Deploying instrument to slot {self.slot}")
            self.session.get(f"slot{self.slot}", self.operation_group)
            self._logger.info(f"{self.__class__.__name__} successfully deployed to slot {self.slot}")


class Moku:
    """
    Moku base class. This class does all the heavy lifting required to
    deploy and control instruments.
    """

    def __init__(
        self,
        ip,
        force_connect=False,
        ignore_busy=False,
        persist_state=False,
        connect_timeout=15,
        read_timeout=30,
        **kwargs,
    ) -> None:

        self._am_owner = False
        logger.info(f"Initializing Moku connection to {ip}")
        logger.debug(f"Connection parameters: force_connect={force_connect}, ignore_busy={ignore_busy}, persist_state={persist_state}")

        try:
            self.session = RequestSession(ip, connect_timeout, read_timeout, **kwargs)
            logger.debug("Session created, claiming ownership")
            self.claim_ownership(force_connect, ignore_busy, persist_state)

            props = self.describe()
            logger.debug(f"Device properties: hardware={props.get('hardware')}, mokuOS={props.get('mokuOS')}")

            if kwargs.get("no_check_version", False):
                pass
            else:
                # TODO: Split the CLI version check from the MokuOS version check?
                if MOKU_CLI_PATH:
                    # If mokucli is found, check it's compatible. If it's not found
                    # then we're likely to fail later like uploading bitstreams.
                    check_mokucli_version(MOKU_CLI_PATH)
                if "proxy_version" not in props:
                    raise IncompatibleMokuException(
                        f"Incompatible MokuOS version, this version of "
                        f"package supports MokuOS {COMPAT_MOKUOS}."
                    )
                if int(props["proxy_version"]) > SUPPORTED_PROXY_VERSION:
                    raise IncompatiblePackageException(
                        "Incompatible Moku package, please update the package using pip"
                    )
                elif int(props["proxy_version"]) < SUPPORTED_PROXY_VERSION:
                    raise IncompatibleMokuException(
                        "You are using an old version of MokuOS. "
                        "Please update to the latest version using the Moku Desktop app or mokucli."
                    )
        except (IncompatibleMokuException, IncompatiblePackageException):
            self.relinquish_ownership()
            raise
        except ConnectionError as e:
            self.relinquish_ownership()
            logger.error(f"Connection failed to {ip}: {e}")
            raise MokuNotFound("Could not connect to Moku")
        except Exception as e:
            self.relinquish_ownership()
            logger.error(f"Unexpected error during initialization: {e}")
            raise MokuException(f"An unexpected error occurred during initialization: {e}")

        self.mokuOS_version: str = props["mokuOS"]
        self.hardware: str = props["hardware"].replace(":", "").lower()
        self.bitstreams = props["bitstreams"]
        self.manage_bitstreams = kwargs.get("manage_bitstreams", True)
        logger.info(f"Successfully connected to {self.hardware} running MokuOS {self.mokuOS_version}")


    def _upload_bitstream_if_required(self, bs_name, rmt_chksum, bs_path=None) -> None:
        logger.debug(f"Checking bitstream {bs_name} (remote checksum: {rmt_chksum[:8] if rmt_chksum else 'None'}...)")
        try:
            bs_path = Path(bs_path or get_bitstream_path(self.mokuOS_version, self.hardware))
            bs_file_name = bs_path / bs_name
            if not bs_file_name.exists():
                logger.error(f"Bitstream file not found: {bs_file_name}")
                raise MokuException(f"Cannot find {bs_file_name}")

            with tarfile.open(bs_file_name, mode="r") as _bar:
                if "MANIFEST" not in _bar.getnames():
                    raise NoInstrumentBitstream(
                        f"MANIFEST file is missing in the bitstream {bs_file_name}."
                    )
                bs_man_file = _bar.extractfile("MANIFEST")
                if not bs_man_file:
                    raise NoInstrumentBitstream(
                        f"Failed to extract MANIFEST file from the bitstream {bs_file_name}."
                    )
                bs_manifest = json.loads(bs_man_file.read())
                local_chksum = bs_manifest["items"][0]["sha256"]
                if not (rmt_chksum and local_chksum == rmt_chksum):
                    logger.info(f"Uploading bitstream {bs_name} (checksum mismatch or missing)")
                    self.upload("bitstreams", bs_name, open(bs_file_name, "rb").read())
                else:
                    logger.debug(f"Bitstream {bs_name} already up to date")

        except (NoInstrumentBitstream, MokuException) as e:
            self.relinquish_ownership()
            raise NoInstrumentBitstream(f"Instrument files not available, please run `mokucli instrument download {self.mokuOS_version}` to download latest instrument data")

        except Exception as e:
            self.relinquish_ownership()
            raise MokuException(f"An unexpected error occurred while uploading bitstream: {e}")


    def upload_bitstream(self, name, bs_path=None):
        if self.manage_bitstreams:
            name = f"{name}.bar"
            exists = [b[1] for b in self.bitstreams.items() if b[0] == name]
            rmt_chksum = exists[0] if exists else None
            self._upload_bitstream_if_required(name, rmt_chksum, bs_path)

    def set_connect_timeout(self, value):
        "Sets requests session connect timeout"
        if not isinstance(value, tuple([int, float])):
            raise ValueError(
                "set_connect_timeout value should be " "either integer or float"
            )
        self.session.connect_timeout = value

    def set_read_timeout(self, value):
        "Sets requests session read timeout"
        if not isinstance(value, tuple([int, float])):
            raise ValueError("read_timeout value should be either " "integer or float")
        self.session.read_timeout = value

    def platform(self, platform_id):
        "Configures platform for the given ID"
        operation = f"platform/{platform_id}"
        self.upload_bitstream(f"{platform_id:02}-000")
        for i in range(0, platform_id):
            self.upload_bitstream(f"{platform_id:02}-000-{i:02}")
        return self.session.get("moku", operation)

    def claim_ownership(
        self, force_connect=True, ignore_busy=False, persist_state=False
    ):
        """
        Claim the ownership of Moku.

        :type force_connect: `boolean`
        :param force_connect: Force connection to Moku disregarding any existing connections

        :type ignore_busy: `boolean`
        :param ignore_busy: Ignore the state of instrument including any in progress data logging sessions and proceed with the deployment # noqa

        :type persist_state: `boolean`
        :param persist_state: When true, tries to retain the previous state of the instrument(if available) # noqa

        """
        operation = "claim_ownership"
        params = dict(
            force_connect=force_connect,
            ignore_busy=ignore_busy,
            persist_state=persist_state,
        )
        logger.debug(f"Claiming ownership with params: {params}")
        ret = self.session.post("moku", operation, params)
        self._am_owner = True
        logger.info("Successfully claimed ownership of Moku")
        return ret

    def relinquish_ownership(self):
        """
        Relinquish the ownership of Moku.
        """
        operation = "relinquish_ownership"
        if hasattr(self, "_am_owner") and self._am_owner:
            logger.debug("Relinquishing ownership")
            ret = self.session.post("moku", operation)
            self._am_owner = False
            logger.info("Successfully relinquished ownership")
        else:
            logger.debug("Not owner, skipping relinquish")
            ret = None
        return ret

    def __enter__(self):
        """
        Enter the runtime context for the Moku object.

        Returns the Moku instance for use in the with statement.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the runtime context for the Moku object.

        Automatically relinquishes ownership when exiting the context.
        """
        if exc_type:
            logger.debug(f"Exiting context with exception: {exc_type.__name__}: {exc_value}")
        else:
            logger.debug("Exiting context normally")
        self.relinquish_ownership()
        return False

    def name(self):
        """
        name.
        """
        operation = "name"
        return self.session.get("moku", operation)

    def serial_number(self):
        """
        serial_number.
        """
        operation = "serial_number"
        return self.session.get("moku", operation)

    def summary(self):
        """
        summary.
        """
        operation = "summary"
        return self.session.get("moku", operation)

    def describe(self):
        """
        describe.
        """
        operation = "describe"
        return self.session.get("moku", operation)

    def calibration_date(self):
        """
        calibration_date.
        """
        operation = "calibration_date"
        return self.session.get("moku", operation)

    def firmware_version(self):
        """
        .. deprecated:: 3.4.0
        MokuOS version.
        """
        print("Warning: firmware_version() is deprecated, use mokuos_version() instead")
        return self.mokuos_version()

    def mokuos_version(self):
        """
        MokuOS version.
        """
        operation = "mokuos_version"
        return self.session.get("moku", operation)

    def get_power_supplies(self):
        """
        get_power_supplies.
        """
        operation = "get_power_supplies"
        return self.session.get("moku", operation)

    def get_power_supply(self, id):
        """
        get_power_supply.

        :type id: `integer`
        :param id: ID of the power supply

        """
        operation = "get_power_supply"
        params = dict(
            id=id,
        )
        return self.session.post("moku", operation, params)

    def set_power_supply(self, id, enable=True, voltage=3, current=0.1):
        """
        set_power_supply.

        :type id: `integer`
        :param id: ID of the power supply to configure

        :type enable: `boolean`
        :param enable: Enable/Disable power supply

        :type voltage: `number`
        :param voltage: Voltage set point

        :type current: `number`
        :param current: Current set point

        """
        operation = "set_power_supply"
        params = dict(
            id=id,
            enable=enable,
            voltage=voltage,
            current=current,
        )
        return self.session.post("moku", operation, params)

    def get_external_clock(self):
        """
        get_external_clock.
        """
        operation = "get_external_clock"
        return self.session.get("moku", operation)

    def set_external_clock(self, enable=True):
        """
        set_external_clock.

        :type enable: `boolean`
        :param enable: Switch between external and internal reference clocks

        """
        operation = "set_external_clock"
        params = dict(
            enable=enable,
        )
        return self.session.post("moku", operation, params)

    def get_blended_clock(self):
        """
        get_blended_clock.
        """
        operation = 'get_blended_clock'
        return self.session.get("moku", operation)

    def set_blended_clock(self, freq_ref_enable=None, freq_ref_frequency=None, sync_ref_enable=None, sync_ref_source=None, strict=True):
        """
        set_blended_clock.

        :type freq_ref_enable: `boolean`
        :param freq_ref_enable: Enable external frequency reference

        :type freq_ref_frequency: `string` ['10MHz', '100MHz']
        :param freq_ref_frequency: Frequency of external frequency reference

        :type sync_ref_enable: `boolean`
        :param sync_ref_enable: Enable synchronization reference

        :type sync_ref_source: `string` [ 'GNSS', 'Ext']
        :param sync_ref_source: Source of synchronization reference

        """
        operation = 'set_blended_clock'
        params = dict(
            freq_ref_enable = freq_ref_enable,
            freq_ref_frequency = freq_ref_frequency,
            sync_ref_enable = sync_ref_enable,
            sync_ref_source = sync_ref_source
        )
        return self.session.post('moku', operation, params)

    def upload(self, target, file_name, data):
        """
        Upload files to bitstreams, ssd, logs, persist.

        :type target: `string`, (bitstreams, ssd, logs, persist, media)
        :param target: Destination where the file should be uploaded to.

        :type file_name: `string`
        :param file_name: Name of the file to be uploaded

        :type data: `bytes`
        :param data: File content

        """
        operation = f"upload/{file_name}"
        return self.session.post_file(target, operation, data)

    def delete(self, target, file_name):
        """
        Delete files from bitstreams, ssd, logs, persist.

        :type target: `string`, (bitstreams, ssd, logs, persist, media)
        :param target: Destination where the file should be uploaded to.

        :type file_name: `string`
        :param file_name: Name of the file to be deleted

        """
        operation = f"delete/{file_name}"
        return self.session.delete_file(target, operation)

    def list(self, target):
        """
        List files at bitstreams, ssd, logs, persist.

        :type target: `string`, (bitstreams, ssd, logs, persist, media)
        :param target: Target directory to list files for

        """
        operation = "list"
        return self.session.get(target, operation)

    def download(self, target, file_name, local_path):
        """
        Download files from bitstreams, ssd, logs, persist.

        :type target: `string`, (bitstreams, ssd, logs, persist, media)
        :param target: Destination where the file should be downloaded from.

        :type file_name: `string`
        :param file_name: Name of the file to be downloaded

        :type local_path: `string`
        :param local_path: Local path to download the file

        """
        operation = f"download/{file_name}"
        return self.session.get_file(target, operation, local_path)

    def modify_hardware(self, data=None):
        """
        CAUTION: Never use to update the state of the Moku
        Raw access to Moku hardware state
        """
        if data is None:
            data = {}
        return self.session.post("moku", "modify_hardware", data)

    def modify_calibration(self, data=None):
        """
        Query or update the calibration coefficients
        """
        if data is None:
            data = {}
        return self.session.post("moku", "modify_calibration", data)

    def set_configuration(self, data=None):
        """
        Update the Moku device/network configuration.
        """
        if data is None:
            data = {}
        return self.session.post("moku", "modify_calibration", data)

    def get_configuration(self):
        """
        Retreive the Moku device/network configuration.
        """
        return self.session.get("moku", "get_configuration")

    def shutdown(self):
        """
        Shutdown the Moku device.
        """
        return self.session.post_to_v2("hwstate", {"power": "shutdown"})["power"]

    def reboot(self):
        """
        Reboot the Moku device.
        """
        return self.session.post_to_v2("hwstate", {"power": "reboot"})["power"]
