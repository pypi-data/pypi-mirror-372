import json

from moku import Moku, MultiInstrumentSlottable
from moku.exceptions import StreamException
from moku.instruments._stream import StreamInstrument


class Datalogger(MultiInstrumentSlottable, Moku, StreamInstrument):
    """
    Datalogger instrument object.

    The Data logger instrument provides file logging of
    time-series voltage data. It contains a built-in
    Waveform Generator that can  control the analog outputs
    as well.

    Read more at https://apis.liquidinstruments.com/reference/datalogger

    """

    INSTRUMENT_ID = 7
    OPERATION_GROUP = "datalogger"

    def __init__(
        self,
        ip=None,
        serial=None,
        force_connect=False,
        ignore_busy=False,
        persist_state=False,
        connect_timeout=15,
        read_timeout=30,
        slot=None,
        multi_instrument=None,
        **kwargs,
    ):
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
            **kwargs,
        )
        StreamInstrument.__init__(self, self.mokuOS_version)

    @classmethod
    def for_slot(cls, slot, multi_instrument):
        """Configures instrument at given slot in multi instrument mode"""
        return cls(slot=slot, multi_instrument=multi_instrument)

    def set_frontend(self, channel, impedance, coupling, range, strict=True):
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

        :type range: `string` ['100mVpp', '400mVpp', '1Vpp', '2Vpp', '4Vpp', '10Vpp', '40Vpp', '50Vpp'] # noqa
        :param range: Input range

        """
        operation = "set_frontend"
        params = dict(
            strict=strict,
            channel=channel,
            impedance=impedance,
            coupling=coupling,
            range=range,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

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
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_acquisition_mode(self, mode="Normal", strict=True):
        """
        set_acquisition_mode.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type mode: `string` ['Normal', 'Precision', 'DeepMemory', 'PeakDetect'] # noqa
        :param mode: Acquisition Mode

        """
        operation = "set_acquisition_mode"
        params = dict(strict=strict, mode=mode)
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_acquisition_mode(self):
        """
        get_acquisition_mode.
        """
        operation = "get_acquisition_mode"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def set_samplerate(self, sample_rate, strict=True):
        """
        set_samplerate.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type sample_rate: `number` [10, 1e6]
        :param sample_rate: Target samples per second

        """
        operation = "set_samplerate"
        params = dict(
            strict=strict,
            sample_rate=sample_rate,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_samplerate(self):
        """
        get_samplerate.
        """
        operation = "get_samplerate"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def disable_channel(self, channel, disable=True, strict=True):
        """
        .. deprecated:: 3.1.1
        Use `enable_input` instead.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type disable: `boolean`
        :param disable: Boolean value to enable/disable

        """
        operation = "disable_channel"
        params = dict(
            strict=strict,
            channel=channel,
            disable=disable,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def enable_input(self, channel, enable=True, strict=True):
        """
        enable_input.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type enable: `boolean`
        :param enable: Enable input signal

        """
        operation = "enable_input"
        params = dict(
            strict=strict,
            channel=channel,
            enable=enable,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def start_logging(
        self,
        duration=60,
        delay=0,
        file_name_prefix="",
        comments="",
        trigger_source=None,
        trigger_level=None,
        strict=True,
        sample_rate=None,
    ):
        """
        start_logging.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type duration: `double` Sec (defaults to 60)
        :param duration: Duration to log for

        :type delay: `integer` Sec (defaults to 0)
        :param delay: Delay the start by

        :type trigger_source: `string` ['ChannelA', 'ChannelB', 'ChannelC', 'ChannelD', 'Input1', 'Input2', 'Input3', 'Input4', 'Output1', 'Output2', 'Output3', 'Output4', 'External'] # noqa
        :param trigger_source: Trigger source

        :type trigger_level: `number` [-5V, 5V]  (defaults to 0)
        :param trigger_level: Trigger level

        :type file_name_prefix: `string`
        :param file_name_prefix: Optional file name prefix

        :type comments: `string`
        :param comments: Optional comments to be included


        .. important::
            It is recommended **not** to relinquish the ownership of the
            device until logging session is completed

        """
        operation = "start_logging"
        params = dict(
            strict=strict,
            duration=duration,
            sample_rate=sample_rate,
            delay=delay,
            trigger_source=trigger_source,
            trigger_level=trigger_level,
            file_name_prefix=file_name_prefix,
            comments=comments,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def stop_logging(self):
        """
        stop_logging.
        """
        operation = "stop_logging"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def summary(self):
        """
        summary.
        """
        operation = "summary"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def generate_waveform(
        self,
        channel,
        type,
        amplitude=1,
        frequency=10000,
        offset=0,
        phase=0,
        duty=None,
        symmetry=None,
        dc_level=None,
        edge_time=None,
        pulse_width=None,
        strict=True,
    ):
        """
        generate_waveform.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type type: `string` ['Off', 'Sine', 'Square', 'Ramp', 'Pulse', 'Noise', 'DC'] # noqa
        :param type: Waveform type

        :type amplitude: `number` [4e-3V, 10V]  (defaults to 1)
        :param amplitude: Waveform peak-to-peak amplitude

        :type frequency: `number` [1e-3Hz, 20e6Hz]  (defaults to 10000)
        :param frequency: Waveform frequency

        :type offset: `number` [-5V, 5V]  (defaults to 0)
        :param offset: DC offset applied to the waveform

        :type phase: `number` [0Deg, 360Deg]  (defaults to 0)
        :param phase: Waveform phase offset

        :type duty: `number` [0.0%, 100.0%]
        :param duty: Duty cycle as percentage (Only for Square wave)

        :type symmetry: `number` [0.0%, 100.0%]
        :param symmetry: Fraction of the cycle rising

        :type dc_level: `number`
        :param dc_level: DC Level. (Only for DC waveform)

        :type edge_time: `number` [16e-9, pulse width]
        :param edge_time: Edge-time of the waveform (Only for Pulse wave)

        :type pulse_width: `number`
        :param pulse_width: Pulse width of the waveform (Only for Pulse wave)

        """
        operation = "generate_waveform"
        params = dict(
            strict=strict,
            channel=channel,
            type=type,
            amplitude=amplitude,
            frequency=frequency,
            offset=offset,
            phase=phase,
            duty=duty,
            symmetry=symmetry,
            dc_level=dc_level,
            edge_time=edge_time,
            pulse_width=pulse_width,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def sync_output_phase(self):
        """
        sync_output_phase.
        """
        operation = "sync_output_phase"
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation)

    def set_output_load(self, channel, load, strict=True):
        """
        .. deprecated:: 3.1.1
        Use `set_output_termination` instead.

        set_output_load.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type load: `string` ['1MOhm', '50Ohm']
        :param load: Output load

        """
        operation = "set_output_load"
        params = dict(
            strict=strict,
            channel=channel,
            load=load,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_output_load(self, channel):
        """
        .. deprecated:: 3.1.1
        Use `get_output_termination` instead.

        get_output_load.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_output_load"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_output_termination(self, channel, termination, strict=True):
        """
        set_output_termination.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type termination: `string` ['HiZ', '50Ohm']
        :param termination: Output termination

        """
        operation = "set_output_termination"
        params = dict(
            strict=strict,
            channel=channel,
            termination=termination,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_output_termination(self, channel):
        """
        get_output_termination.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_output_termination"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def logging_progress(self):
        """
        logging_progress.
        """
        operation = "logging_progress"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def start_streaming(
        self, duration=None, sample_rate=None, trigger_source=None, trigger_level=None
    ):
        """
        start_streaming.

        :type duration: `double`
        :param duration: Duration in second(s) to stream for

        :type sample_rate: `number` [10, 1e6]
        :param sample_rate: Target samples per second

        :type trigger_source: `string` ['ChannelA', 'ChannelB', 'ChannelC', 'ChannelD', 'Input1', 'Input2', 'Input3', 'Input4', 'Output1', 'Output2', 'Output3', 'Output4', 'External'] # noqa
        :param trigger_source: Trigger source

        :type trigger_level: `number` [-5V, 5V]  (defaults to 0)
        :param trigger_level: Trigger level

        """
        super().start_streaming()
        operation = "start_streaming"
        params = dict(
            duration=duration,
            sample_rate=sample_rate,
            trigger_source=trigger_source,
            trigger_level=trigger_level,
        )
        response = self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )
        self.stream_id = response["stream_id"]
        self.ip_address = self.session.ip_address
        return response

    def stop_streaming(self):
        """
        stop_streaming.

        """
        operation = "stop_streaming"
        response = self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation
        )
        self.stream_id = None
        return response

    def get_chunk(self):
        """
        get_chunk.

        Get the next raw chunk from the streaming session

        """
        data = {"stream_id": {self.stream_id: {"topic": f"logformat{self.slot-1}"}}}
        result = self.session.post_to_v2_raw("get_chunk", params=data)

        if result.status_code != 200:
            raise StreamException("Error fetching stream.")

        try:
            error = json.loads(result.content)
            raise StreamException(error.get("error", error))
        except StreamException as e:
            raise e
        except Exception:
            return result.content

    def get_stream_status(self):
        """
        get_stream_status.

        """
        operation = "get_stream_status"

        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation)
