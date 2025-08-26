from moku import Moku
from moku.exceptions import MokuException
from moku.utilities import find_moku_by_serial
from moku import instruments
from inspect import getmembers, isclass


class MultiInstrument(Moku):
    """
    Multi Instrument Mode.
    """

    def __init__(
        self,
        ip=None,
        serial=None,
        platform_id=None,
        force_connect=False,
        ignore_busy=False,
        persist_state=False,
        connect_timeout=15,
        read_timeout=30,
        **kwargs,
    ):
        self.operation_group = "mim"
        if not platform_id:
            raise Exception("platform_id cannot be empty")
        self.platform_id = platform_id
        if not any([ip, serial]):
            raise MokuException("IP (or) Serial is required")
        if serial:
            ip = find_moku_by_serial(serial)

        super().__init__(
            ip=ip,
            force_connect=force_connect,
            ignore_busy=ignore_busy,
            persist_state=persist_state,
            connect_timeout=connect_timeout,
            read_timeout=read_timeout,
            **kwargs,
        )

        self.platform(self.platform_id)

    def set_instrument(self, slot, instrument, **kwargs):
        if not 1 <= slot <= self.platform_id:
            raise Exception(f"Invalid slot for {self.platform_id} " f"slot platform")

        if instrument not in [x[1] for x in getmembers(instruments, isclass)]:
            raise Exception(f"{instrument} is not a valid instrument")

        empty_slots = [
            i for i, v in enumerate(self.get_instruments()) if i + 1 != slot and v == ""
        ]

        for i in empty_slots:
            self.upload_bitstream(f"{self.platform_id:02}-000-{i:02}")

        return instrument.for_slot(slot, self, **kwargs)

    def set_connections(self, connections):
        """
        set_connections.

        :type connections: `list`
        :param connections: List of map of source and destination points.

        """
        operation = "set_connections"
        params = dict(
            connections=connections,
        )
        return self.session.post(self.operation_group, operation, params)

    def set_frontend(self, channel, impedance, coupling, attenuation=None, gain=None, strict=True):
        """
        set_frontend.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type impedance: `string` ['1MOhm', '50Ohm']
        :param impedance: Input impedance

        :type coupling: `string` ['AC', 'DC']
        :param coupling: Input coupling

        :type attenuation: `string` ['-20dB', '0dB', '14dB', '20dB', '32dB', '40dB'] # noqa
        :param attenuation: Input attenuation.

        """
        operation = "set_frontend"
        params = dict(
            strict=strict,
            channel=channel,
            impedance=impedance,
            coupling=coupling,
            attenuation=attenuation,
            gain=gain,
        )
        return self.session.post(self.operation_group, operation, params)

    def set_output(self, channel, output_gain, strict=True):
        """
        set_output.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type output_gain: `string` ['0dB', '14dB']
        :param output_gain: Output Gain

        """
        operation = "set_output"
        params = dict(
            strict=strict,
            channel=channel,
            output_gain=output_gain,
        )
        return self.session.post(self.operation_group, operation, params)

    def set_dio(self, direction=None, direction_map=None, strict=True):
        """
        set_dio.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type direction: `list`
        :param direction: List of DIO directions. 0 for In and 1 for Out, defaults to all 0's (In) # noqa

        :type direction_map: `list`
        :param direction_map: List of map of DIO directions

        """
        operation = "set_dio"
        params = dict(
            strict=strict,
            direction=direction,
            direction_map=direction_map,
        )
        return self.session.post(self.operation_group, operation, params)

    def sync(self):
        """
        sync.
        """
        operation = "sync"
        return self.session.get(self.operation_group, operation)

    def get_connections(self):
        """
        get_connections.
        """
        operation = "get_connections"
        return self.session.get(self.operation_group, operation)

    def get_instruments(self):
        """
        get_instruments.
        """
        operation = "get_instruments"
        return self.session.get(self.operation_group, operation)

    def get_frontend(self, channel):
        """
        get_frontend.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_frontend"
        params = dict(
            channel=channel,
        )
        return self.session.post(self.operation_group, operation, params)

    def get_output(self, channel):
        """
        get_output.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_output"
        params = dict(
            channel=channel,
        )
        return self.session.post(self.operation_group, operation, params)

    def get_dio(self, port = None):
        """
        get_dio.
        
        :type port: `integer`
        :param port: Target DIO port.
        """
        operation = "get_dio"
        params = dict(
            port=port
        )
        return self.session.post(self.operation_group, operation, params)
