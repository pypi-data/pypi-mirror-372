import json

from moku import Moku, MultiInstrumentSlottable
from moku.exceptions import StreamException
from moku.instruments._stream import StreamInstrument


class Phasemeter(MultiInstrumentSlottable, Moku, StreamInstrument):
    """
    Phasemeter instrument object.

    The Phasemeter instrument is used to measure the
    amplitude and change in phase of periodic input
    signals. Using the auto-acquire feature, it can
    automatically lock to input frequencies in the
    range of 2-200MHz and track phase with a
    bandwidth of 10kHz.

    Read more at https://apis.liquidinstruments.com/reference/phasemeter

    """

    INSTRUMENT_ID = 3
    OPERATION_GROUP = "phasemeter"

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

    def summary(self):
        """
        summary.
        """
        operation = "summary"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def set_defaults(self):
        """
        set_defaults.
        """
        operation = "set_defaults"
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation)

    def reacquire(self):
        """
        reacquire.
        """
        operation = "reacquire"
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation)

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

    def set_acquisition_speed(self, speed, strict=True):
        """
        set_acquisition_speed.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type speed: `string` ['30Hz', '37Hz', '119Hz', '150Hz', '477Hz',  '596Hz', '1.9kHz', '2.4kHz', '15.2kHz', '19.1kHz', '122kHz', '152kHz'] # noqa
        :param speed: Acquisition Speed

        """
        operation = "set_acquisition_speed"
        params = dict(strict=strict, speed=speed)
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_pm_loop(
        self, channel, auto_acquire=False, frequency=1e6, bandwidth="1kHz", strict=True
    ):
        """
        set_pm_loop.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type auto_acquire: `boolean`
        :param auto_acquire: Auto acquire frequency

        :type frequency: `number`
        :param frequency: Initial locking frequency of the designated channel

        :type bandwidth: `string` ['1Hz', '10Hz', '100Hz', '1kHz', '10kHz', '100kHz', '1MHz'] # noqa
        :param bandwidth: Bandwidth

        """
        operation = "set_pm_loop"
        params = dict(
            strict=strict,
            channel=channel,
            auto_acquire=auto_acquire,
            frequency=frequency,
            bandwidth=bandwidth,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_pm_loop(self, channel):
        """
        get_pm_loop.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_pm_loop"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_auto_acquired_frequency(self, channel, strict=True):
        """
        get_auto_acquired_frequency.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_auto_acquired_frequency"
        params = dict(
            strict=strict,
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def generate_output(
        self,
        channel,
        signal,
        amplitude=0.5,
        frequency=1e6,
        frequency_multiplier=1,
        phase=0,
        offset=0,
        phase_locked=False,
        scaling=0.001,
        output_range=None,
        strict=True,
    ):
        """
        generate_output.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type signal: `string` ['Sine', 'Phase', 'FrequencyOffset', 'Amptitude'] # noqa
        :param signal: Type of output signal

        :type amplitude: `number`
        :param amplitude: Waveform peak-to-peak amplitude

        :type frequency: `number`
        :param frequency: Frequency of the wave

        :type frequency_multiplier: `number`
        :param frequency_multiplier: Frequency multiplier

        :type phase: `number`
        :param phase: Phase offset of the wave

        :type offset: `number`
        :param offset: Offset offset of the wave

        :type phase_locked: `boolean`
        :param phase_locked: Locks the phase of the generated sinewave to the measured phase of the input signal # noqa

        :type scaling: `number`
        :param scaling: Scaling for phase, frequency offset and amplitude

        :type output_range: `string` ['2Vpp', '10Vpp']
        :param output_range: Output range

        """
        operation = "generate_output"
        params = dict(
            strict=strict,
            channel=channel,
            signal=signal,
            amplitude=amplitude,
            frequency=frequency,
            frequency_multiplier=frequency_multiplier,
            phase=phase,
            offset=offset,
            phase_locked=phase_locked,
            scaling=scaling,
            output_range=output_range,
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

    def disable_output(self, channel, strict=True):
        """
        disable_output.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "disable_output"
        params = dict(
            strict=strict,
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def disable_input(self, channel):
        """
        .. deprecated:: 3.1.1
        Use `enable_input` instead.

        disable_input.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "disable_input"
        params = dict(
            channel=channel,
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

    def zero_phase(self, channel):
        """
        zero_phase.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "zero_phase"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def enable_freewheeling(self, enable=True, strict=True):
        """
        enable_freewheeling.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type enable: `boolean`
        :param enable: Enable free wheeling

        """
        operation = "enable_freewheeling"
        params = dict(
            strict=strict,
            enable=enable,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def enable_single_input(self, enable=True, strict=True):
        """
        enable_single_input.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type enable: `boolean`
        :param enable: Sends the signal from the first input to all phasemeter channels # noqa

        """
        operation = "enable_single_input"
        params = dict(
            strict=strict,
            enable=enable,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_phase_wrap(self, value="Off", strict=True):
        """
        set_phase_wrap.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type value: `string` ['Off', '1pi', '2pi', '4pi']
        :param value: Wraps the phase output at a particular value

        """
        operation = "set_phase_wrap"
        params = dict(strict=strict, value=value)
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_auto_reset(self, value="Off", strict=True):
        """
        set_auto_reset.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type value: `string` ['Off', '1pi', '2pi', '4pi']
        :param value: Reset the phase output to zero when it exceeds a particular value # noqa

        """
        operation = "set_auto_reset"
        params = dict(strict=strict, value=value)
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_data(self, timeout=None, wait_reacquire=None):
        """
        get_data.

        :type timeout: `number` Seconds (defaults to 60)
        :param timeout: Wait for n seconds to receive a data frame

        :type wait_reacquire: `boolean`
        :param wait_reacquire: Wait until new dataframe is reacquired


        .. important::
            Default timeout for reading the data is 10 seconds. It
            can be increased by setting the read_timeout property of
            session object.

            Example: ``i.session.read_timeout=100`` (in seconds)

        """
        operation = "get_data"
        params = dict(
            timeout=timeout,
            wait_reacquire=wait_reacquire,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def start_logging(
        self, duration=60, delay=0, file_name_prefix="", comments="", strict=True, acquisition_speed=None
    ):
        """
        start_logging.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type duration: `integer` Sec (defaults to 60)
        :param duration: Duration to log for

        :type delay: `integer` Sec (defaults to 0)
        :param delay: Delay the start by

        :type file_name_prefix: `string`
        :param file_name_prefix: Optional file name prefix

        :type comments: `string`
        :param comments: Optional comments to be included

        :type acquisition_speed: `string` ['30Hz', '37Hz', '119Hz', '150Hz', '477Hz',  '596Hz', '1.9kHz', '2.4kHz', '15.2kHz', '19.1kHz', '122kHz', '152kHz']
        :param acquisition_speed: Acquisition speed (e.g. "30Hz")

        """
        operation = "start_logging"
        params = dict(
            strict=strict,
            duration=duration,
            delay=delay,
            file_name_prefix=file_name_prefix,
            comments=comments,
            acquisition_speed=acquisition_speed,
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

    def get_acquisition_speed(self):
        """
        get_acquisition_speed.
        """
        operation = "get_acquisition_speed"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def logging_progress(self):
        """
        logging_progress.
        """
        operation = "logging_progress"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def start_streaming(self, duration=None, acquisition_speed=None):
        """
        start_streaming.

        :type duration: `integer`
        :param duration: Duration in second(s) to stream for

        :type acquisition_speed: `string`
        :param acquisition_speed: Acquisition speed (e.g. "30Hz")

        """
        super().start_streaming()
        operation = "start_streaming"
        params = dict(duration=duration, acquisition_speed=acquisition_speed)
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

    def get_stream_status(self):
        """
        get_stream_status.

        """
        operation = "get_stream_status"

        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation)

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
