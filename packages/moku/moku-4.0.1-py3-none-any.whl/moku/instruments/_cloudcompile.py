import tarfile
import tempfile
from pathlib import Path

from moku import Moku, MultiInstrumentSlottable
from moku.exceptions import MokuException, NoInstrumentBitstream


class CloudCompile(MultiInstrumentSlottable, Moku):
    """
    Cloud Compile - Custom Instrument

    """

    INSTRUMENT_ID = 255
    OPERATION_GROUP = "cloudcompile"

    def __init__(
        self,
        ip=None,
        serial=None,
        force_connect=False,
        ignore_busy=False,
        persist_state=False,
        bitstream=None,
        connect_timeout=15,
        read_timeout=30,
        slot=None,
        multi_instrument=None,
        **kwargs,
    ):
        assert bitstream, "Bitstream package path is required for Cloud Compile"

        bitstream_path = Path(bitstream)
        if not bitstream_path.exists():
            raise FileNotFoundError(f"Bitstream package not found at {bitstream_path}")

        with tempfile.TemporaryDirectory(prefix="moku_cloudcompile_") as temp_dir:
            # Open and extract the tar/tar.gz file
            with tarfile.open(bitstream_path, mode="r:*") as tar:
                tar.extractall(temp_dir)

            try:
                self._init_instrument(
                    ip=ip,
                    serial=serial,
                    force_connect=force_connect,
                    ignore_busy=ignore_busy,
                    persist_state=persist_state,
                    connect_timeout=connect_timeout,
                    read_timeout=read_timeout,
                    slot=slot,
                    multi_instrument=multi_instrument,
                    bs_path=temp_dir,
                    **kwargs,
                )
            except NoInstrumentBitstream:
                # Intercept this exception to change the error message. By default this will show the
                # "run mokucli instrument download" message, which is not applicable here.
                raise MokuException(f"Failed to initialize CloudCompile instrument. Please check the bitstream package and try again (tried {bitstream_path.absolute()})")

    @classmethod
    def for_slot(cls, slot, multi_instrument, **kwargs):
        """Configures instrument at given slot in multi instrument mode"""
        bitstream = kwargs.get("bitstream")
        return cls(slot=slot, multi_instrument=multi_instrument, bitstream=bitstream)

    def set_controls(self, controls, strict=True):
        """
        set_controls.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type controls: `list`
        :param controls: List of control map(pair of id, value)

        """
        operation = "set_controls"
        params = dict(
            strict=strict,
            controls=controls,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_control(self, idx, value, strict=True):
        """
        set_control.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type idx: `integer`
        :param idx: Control ID(0 indexed)

        :type value: `integer`
        :param value: Register value

        """
        operation = "set_control"
        params = dict(
            strict=strict,
            idx=idx,
            value=value,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_control(self, idx, strict=True):
        """
        get_control.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type idx: `integer`
        :param idx: Control ID(0 indexed)

        """
        operation = "get_control"
        params = dict(
            strict=strict,
            idx=idx,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_controls(self):
        """
        get_controls.
        """
        operation = "get_controls"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def set_interpolation(self, channel, enable=True, strict=True):
        """
        set_interpolation.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type enable: `boolean`
        :param enable: Enable/disable interpolation on specified channel

        """
        operation = "set_interpolation"
        params = dict(
            strict=strict,
            channel=channel,
            enable=enable,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def sync(self, mask, strict=True):
        """
        sync.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type mask: `integer`
        :param mask: Mask value

        """
        operation = "sync"
        params = dict(
            strict=strict,
            mask=mask,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_interpolation(self, channel):
        """
        get_interpolation.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_interpolation"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def summary(self):
        """
        summary.
        """
        operation = "summary"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)