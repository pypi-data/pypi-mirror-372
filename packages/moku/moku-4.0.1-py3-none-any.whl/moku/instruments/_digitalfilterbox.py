import json

from moku import Moku, MultiInstrumentSlottable
from moku.exceptions import StreamException
from moku.instruments._stream import StreamInstrument


class DigitalFilterBox(MultiInstrumentSlottable, Moku, StreamInstrument):
    """
    DigitalFilterBox instrument object.

    The Digital Filter Box can interactively design and
    generate different types of infinite impulse  response
    filters with varied sampling rates.

    DigitalFilterBox includes lowpass, highpass, bandpass
    and bandstop filter shapes with different filter types
    including Butterworth, Chebyshev, and Elliptic.

    Read more at https://apis.liquidinstruments.com/reference/dfb

    """

    INSTRUMENT_ID = 6
    OPERATION_GROUP = "digitalfilterbox"

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

    def set_frontend(self, channel, coupling, impedance, attenuation=None, gain=None, strict=True):
        """
        set_frontend.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type coupling: `string` ['AC', 'DC']
        :param coupling: Input coupling

        :type impedance: `string` ['1MOhm', '50Ohm']
        :param impedance: Input impedance

        :type attenuation: `string` ['-20dB', '0dB', '14dB', '20dB', '32dB', '40dB'] # noqa
        :param attenuation: Input attenuation.

        :type gain: `string` ['20dB', '0dB', '-14dB', '-20dB', '-32dB', '-40dB'] # noqa
        :param attenuation: Input gain.

        """
        operation = "set_frontend"
        params = dict(
            strict=strict,
            channel=channel,
            coupling=coupling,
            impedance=impedance,
            attenuation=attenuation,
            gain=gain,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_control_matrix(self, channel, input_gain1, input_gain2, strict=True):
        """
        set_control_matrix.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type input_gain1: `number` [-20, 20]
        :param input_gain1: ADC input gain for Channel 1

        :type input_gain2: `number` [-20, 20]
        :param input_gain2: ADC input gain for Channel 2

        """
        operation = "set_control_matrix"
        params = dict(
            strict=strict,
            channel=channel,
            input_gain1=input_gain1,
            input_gain2=input_gain2,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_monitor(self, monitor_channel, source, strict=True):
        """
        set_monitor.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type monitor_channel: `integer`
        :param monitor_channel: Monitor channel

        :type source: `string` ['None', 'Input1', 'Filter1', 'Output1', 'Input2', 'Filter2', 'Output2', 'Input3', 'Filter3', 'Output3', 'Input4', 'Filter4', 'Output4'] # noqa
        :param source: Monitor channel source.

        """
        operation = "set_monitor"
        params = dict(
            strict=strict,
            monitor_channel=monitor_channel,
            source=source,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def enable_output(
        self, channel, signal=True, output=True, gain_range="0dB", strict=True
    ):
        """
        enable_output.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type signal: `boolean`
        :param signal: Enable output signal

        :type output: `boolean`
        :param output: Enable output

        :type gain_range: `string`
        :param gain_range: Enable output

        """
        operation = "enable_output"
        params = dict(
            strict=strict,
            channel=channel,
            signal=signal,
            output=output,
            gain_range=gain_range,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_input_offset(self, channel, offset, strict=True):
        """
        set_input_offset.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type offset: `number` [-5V, 5V]
        :param offset: Offset

        """
        operation = "set_input_offset"
        params = dict(
            strict=strict,
            channel=channel,
            offset=offset,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_output_offset(self, channel, offset, strict=True):
        """
        set_output_offset.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type offset: `number` [-5V, 5V]
        :param offset: Offset

        """
        operation = "set_output_offset"
        params = dict(
            strict=strict,
            channel=channel,
            offset=offset,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_input_gain(self, channel, gain, strict=True):
        """
        set_input_gain.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type gain: `number` [-40dB, 40dB]
        :param gain: Gain

        """
        operation = "set_input_gain"
        params = dict(
            strict=strict,
            channel=channel,
            gain=gain,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_output_gain(self, channel, gain, strict=True):
        """
        set_output_gain.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type gain: `number` [-40dB, 40dB]
        :param gain: Gain

        """
        operation = "set_output_gain"
        params = dict(
            strict=strict,
            channel=channel,
            gain=gain,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_trigger(
        self,
        type="Edge",
        level=0,
        mode="Auto",
        edge="Rising",
        polarity="Positive",
        width=0.0001,
        width_condition="LessThan",
        nth_event=1,
        holdoff=0,
        hysteresis=1e-3,
        auto_sensitivity=None,
        noise_reject=False,
        hf_reject=False,
        source="ProbeA",
        strict=True,
    ):
        """
        set_trigger.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type type: `string` ['Edge', 'Pulse']
        :param type: Trigger type

        :type level: `number` [-5V, 5V]  (defaults to 0)
        :param level: Trigger level

        :type mode: `string` ['Auto', 'Normal']
        :param mode: Trigger mode

        :type edge: `string` ['Rising', 'Falling', 'Both']
        :param edge: Which edge to trigger on. In Pulse Width modes this specifies whether the pulse is positive (rising) or negative (falling), with the 'both' option being invalid # noqa

        :type polarity: `string` ['Positive', 'Negative']
        :param polarity: Trigger pulse polarity (Pulse mode only)

        :type width: `number` [26e-3Sec, 10Sec]  (defaults to 0.0001)
        :param width: Width of the trigger pulse (Pulse mode only)

        :type width_condition: `string` ['GreaterThan', 'LessThan']
        :param width_condition: Trigger pulse width condition (pulse mode only)

        :type nth_event: `integer` [0, 65535]  (defaults to 1)
        :param nth_event: The number of trigger events to wait for before triggering # noqa

        :type holdoff: `number` [1e-9Sec, 10Sec]  (defaults to 0)
        :param holdoff: The duration to hold-off Oscilloscope trigger post trigger event # noqa

        :type hysteresis: `number` (defaults to 0.1)
        :param hysteresis: Absolute hysteresis around trigger

        :type auto_sensitivity: `boolean`
        :param auto_sensitivity: Configure auto or manual hysteresis for noise rejection.

        :type noise_reject: `boolean`
        :param noise_reject: Configure the Oscilloscope with a small amount of hysteresis to prevent repeated triggering due to noise # noqa

        :type hf_reject: `boolean`
        :param hf_reject: Configure the trigger signal to pass through a low pass filter to smooths out the noise # noqa

        :type source: `string` ['ProbeA', 'ProbeB', 'ProbeC', 'ProbeD', 'External']
        :param source: Trigger Source

        """
        operation = "set_trigger"
        params = dict(
            strict=strict,
            type=type,
            level=level,
            mode=mode,
            edge=edge,
            polarity=polarity,
            width=width,
            width_condition=width_condition,
            nth_event=nth_event,
            holdoff=holdoff,
            hysteresis=hysteresis,
            auto_sensitivity=auto_sensitivity,
            noise_reject=noise_reject,
            hf_reject=hf_reject,
            source=source,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_filter(
        self,
        channel,
        sample_rate,
        shape="Lowpass",
        type="Butterworth",
        low_corner=None,
        high_corner=None,
        pass_band_ripple=None,
        stop_band_attenuation=None,
        order=8,
        strict=True,
    ):
        """
        set_filter.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type sample_rate: `string` ['3.906MHz', '488.3kHz', '61.04kHz', '39.06MHz', '4.883MHz', '305.2kHz', '15.625MHz', '1.9531MHz', '122.07kHz'] # noqa
        :param sample_rate: Sample rate

        :type shape: `string` ['Lowpass', 'Highpass', 'Bandpass', 'Bandstop']
        :param shape: Filter shape

        :type type: `string` ['Butterworth', 'ChebyshevI', 'ChebyshevII', 'Elliptic', 'Cascaded', 'Bessel', 'Gaussian', 'Legendre'] # noqa
        :param type: Filter type

        :type low_corner: `number`
        :param low_corner: Low corner frequency

        :type high_corner: `number`
        :param high_corner: High corner frequency

        :type pass_band_ripple: `number`
        :param pass_band_ripple: Passband ripple

        :type stop_band_attenuation: `number`
        :param stop_band_attenuation: Stopband attenuation

        :type order: `integer`
        :param order: Filter order

        """
        operation = "set_filter"
        params = dict(
            strict=strict,
            channel=channel,
            sample_rate=sample_rate,
            shape=shape,
            type=type,
            low_corner=low_corner,
            high_corner=high_corner,
            pass_band_ripple=pass_band_ripple,
            stop_band_attenuation=stop_band_attenuation,
            order=order,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_custom_filter(
        self, channel, sample_rate, scaling=1, coefficients=None, strict=True
    ):
        """
        set_custom_filter.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type sample_rate: `string` ['3.906MHz', '488.3kHz', '61.04kHz', '39.06MHz', '4.883MHz', '305.2kHz', '15.625MHz', '1.9531MHz', '122.07kHz'] # noqa
        :param sample_rate: Sample rate

        :type scaling: `number`
        :param scaling: Output scaling

        :type coefficients: `list`
        :param coefficients: List of filter stages, where each stage should have six coefficients and each coefficient must be in the range [-4.0, 4.0] # noqa

        """
        operation = "set_custom_filter"
        params = dict(
            strict=strict,
            channel=channel,
            sample_rate=sample_rate,
            scaling=scaling,
            coefficients=coefficients,
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

    def get_control_matrix(self, channel):
        """
        get_control_matrix.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_control_matrix"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_input_offset(self, channel):
        """
        get_input_offset.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_input_offset"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_output_offset(self, channel):
        """
        get_output_offset.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_output_offset"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_input_gain(self, channel):
        """
        get_input_gain.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_input_gain"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_output_gain(self, channel):
        """
        get_output_gain.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_output_gain"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_timebase(self, t1, t2, strict=True):
        """
        set_timebase.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type t1: `number`
        :param t1: Time from the trigger point to the left of screen. This may be negative (trigger on-screen) or positive (trigger off the left of screen).

        :type t2: `number`
        :param t2: Time from the trigger point to the right of screen. (Must be a positive number, i.e. after the trigger event) # noqa

        """
        operation = "set_timebase"
        params = dict(
            strict=strict,
            t1=t1,
            t2=t2,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_hysteresis(self, hysteresis_mode, value=0, strict=True):
        """
        set_hysteresis.

        .. deprecated:: 3.1.1
        Use `hysteresis` parameter of `set_trigger` instead.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type hysteresis_mode: `string` ['Absolute', 'Relative']
        :param hysteresis_mode: Trigger sensitivity hysteresis mode

        :type value: `number`
        :param value: Hysteresis around trigger

        """
        operation = "set_hysteresis"
        params = dict(
            strict=strict,
            hysteresis_mode=hysteresis_mode,
            value=value,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def enable_rollmode(self, roll=True, strict=True):
        """
        enable_rollmode.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type roll: `boolean`
        :param roll: Enable roll

        """
        operation = "enable_rollmode"
        params = dict(
            strict=strict,
            roll=roll,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_data(
        self, timeout=60, wait_reacquire=False, wait_complete=False, measurements=False
    ):
        """
        get_data.

        :type timeout: `number` Seconds (defaults to 60)
        :param timeout: Wait for n seconds to receive a data frame

        :type wait_reacquire: `boolean`
        :param wait_reacquire: Wait until new dataframe is reacquired

        :type wait_complete: `boolean`
        :param wait_complete: Wait until entire frame is available

        :type measurements: `boolean`
        :param measurements: When True, includes available measurements for each channel

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
            wait_complete=wait_complete,
            measurements=measurements,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def save_high_res_buffer(self, comments="", timeout=60):
        """
        save_high_res_buffer.

        :type comments: `string`
        :param comments: Optional comments to be included

        :type timeout: `int`
        :param timeout: Wait for n seconds before trigger event happens to save the buffer # noqa

        """
        operation = "save_high_res_buffer"
        params = dict(comments=comments, timeout=timeout)
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

    def get_samplerate(self):
        """
        get_samplerate.
        """
        operation = "get_samplerate"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def get_acquisition_mode(self):
        """
        get_acquisition_mode.
        """
        operation = "get_acquisition_mode"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def get_timebase(self):
        """
        get_timebase.
        """
        operation = "get_timebase"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def logging_progress(self):
        """
        logging_progress.
        """
        operation = "logging_progress"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def start_logging(
        self,
        duration=60,
        delay=0,
        file_name_prefix="",
        comments="",
        trigger_source=None,
        trigger_level=None,
        mode="Normal",
        rate=None,
        strict=True,
    ):
        """
        start_logging.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type duration: `integer` Sec (defaults to 60)
        :param duration: Duration to log for

        :type delay: `integer` Sec (defaults to 0)
        :param delay: Delay the start by

        :type trigger_source: `string`  ['ProbeA', 'ProbeB', 'ProbeC', 'ProbeD', 'External'] # noqa
        :param trigger_source: Trigger source

        :type trigger_level: `number` [-5V, 5V]  (defaults to 0)
        :param trigger_level: Trigger level

        :type file_name_prefix: `string`
        :param file_name_prefix: Optional file name prefix

        :type comments: `string`
        :param comments: Optional comments to be included

        :type mode: `string` ['Normal', 'Precision', 'DeepMemory', 'PeakDetect'] # noqa
        :param mode: Acquisition Mode

        :type rate: `number`
        :param rate: Acquisition rate

        """
        operation = "start_logging"
        params = dict(
            strict=strict,
            duration=duration,
            delay=delay,
            trigger_source=trigger_source,
            trigger_level=trigger_level,
            file_name_prefix=file_name_prefix,
            comments=comments,
            mode=mode,
            rate=rate,
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

    def start_streaming(
        self,
        duration=None,
        mode="Normal",
        rate=None,
        trigger_source=None,
        trigger_level=None,
    ):
        """
        start_streaming.

        :type duration: `integer`
        :param duration: Duration in second(s) to stream for

        :type mode: `string` ['Normal', 'Precision', 'DeepMemory', 'PeakDetect'] # noqa
        :param mode: Acquisition Mode

        :type rate: `number`
        :param rate: Acquisition rate

        :type trigger_source: `string`  ['ProbeA', 'ProbeB', 'ProbeC', 'ProbeD', 'External'] # noqa
        :param trigger_source: Trigger source

        :type trigger_level: `number` [-5V, 5V]  (defaults to 0)
        :param trigger_level: Trigger level


        """
        super().start_streaming()
        operation = "start_streaming"
        params = dict(
            duration=duration,
            mode=mode,
            rate=rate,
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
