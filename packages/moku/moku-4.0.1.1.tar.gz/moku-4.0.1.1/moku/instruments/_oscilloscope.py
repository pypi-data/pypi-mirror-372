from moku import Moku, MultiInstrumentSlottable


class Oscilloscope(MultiInstrumentSlottable, Moku):
    """
    Oscilloscope instrument object.

    The Oscilloscope instrument provides time-domain views
    of voltages. It contains a built-in Waveform Generator
    that can control the Moku analog outputs as well.

    In normal operation, the Oscilloscope shows the signal
    present on the two analog inputs but it can be set to
    loop back the signals being generated

    Read more at https://apis.liquidinstruments.com/reference/oscilloscope # noqa

    """

    INSTRUMENT_ID = 1
    OPERATION_GROUP = "oscilloscope"

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

    @classmethod
    def for_slot(cls, slot, multi_instrument):
        """Configures instrument at given slot in multi instrument mode"""
        return cls(slot=slot, multi_instrument=multi_instrument)

    def set_defaults(self):
        """
        set_defaults.
        """
        operation = "set_defaults"
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation)

    def sync_output_phase(self):
        """
        sync_output_phase.
        """
        operation = "sync_output_phase"
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

    def set_sources(self, sources, strict=True):
        """
        set_sources.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type sources: `list`
        :param sources: List of sources

        """
        operation = "set_sources"
        params = dict(
            strict=strict,
            sources=sources,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_source(self, channel, source, strict=True):
        """
        set_source.

        :type channel: `integer`
        :param channel: Target channel

        :type source: `string` ['None', 'Input1', 'Input2', 'Input3', 'Input4', 'Output1', 'Output2', 'Output3', 'Output4'] # noqa
        :param source: Set channel data source

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        """
        operation = "set_source"
        params = dict(
            channel=channel,
            source=source,
            strict=strict,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_input_attenuation(self, channel, attenuation, strict=True):
        """
        set_input_attenuation.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type attenuation: `integer`
        :param attenuation: Input attenuation(0.1 to 1000)

        """
        operation = "set_input_attenuation"
        params = dict(
            strict=strict,
            channel=channel,
            attenuation=attenuation,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_sources(self):
        """
        get_sources.
        """
        operation = "get_sources"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def set_interpolation(self, interpolation="SinX", strict=True):
        """
        set_interpolation.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type interpolation: `string` ['Linear', 'SinX', 'Gaussian']
        :param interpolation: Interpolation

        """
        operation = "set_interpolation"
        params = dict(strict=strict, interpolation=interpolation)
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_interpolation(self):
        """
        get_interpolation.
        """
        operation = "get_interpolation"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def disable_input(self, channel, strict=True):
        """
        disable_input.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "disable_input"
        params = dict(
            strict=strict,
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_trigger(
        self,
        type="Edge",
        level=0,
        level_low=0,
        level_high=0.1,
        mode="Auto",
        edge="Rising",
        polarity="Positive",
        width=0.0001,
        width_condition="LessThan",
        nth_event=1,
        holdoff=0,
        hysteresis=1e-3,
        auto_sensitivity=True,
        noise_reject=False,
        hf_reject=False,
        source="Input1",
        strict=True,
    ):
        """
        set_trigger.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type type: `string` ['Edge', 'Pulse', 'Runt']
        :param type: Trigger type

        :type level: `number` [-5V, 5V]  (defaults to 0)
        :param level: Trigger level

        :type levelLow: `number` [-5V, 5V]  (defaults to 0)
        :param level: Low trigger level (Runt mode only)

        :type levelHigh: `number` [-5V, 5V]  (defaults to 0.1)
        :param level: High trigger level (Runt mode only)

        :type mode: `string` ['Auto', 'Normal']
        :param mode: Trigger mode

        :type edge: `string` ['Rising', 'Falling', 'Both']
        :param edge: Which edge to trigger on (Edge and Pulse mode). In Pulse Width modes this specifies whether the pulse is positive (rising) or negative (falling), with the 'both' option being invalid # noqa

        :type polarity: `string` ['Positive', 'Negative']
        :param polarity: Trigger pulse polarity (Runt and Pulse mode)

        :type width: `number` [26e-3Sec, 10Sec]  (defaults to 0.0001)
        :param width: Width of the trigger pulse (Pulse mode only)

        :type width_condition: `string` ['GreaterThan', 'LessThan']
        :param width_condition: Trigger pulse width condition (pulse mode only)

        :type nth_event: `integer` [0, 65535]  (defaults to 1)
        :param nth_event: The number of trigger events to wait for before triggering # noqa

        :type holdoff: `number` [1e-9Sec, 10Sec]  (defaults to 0)
        :param holdoff: The duration to hold-off Oscilloscope trigger post trigger event # noqa

        :type hysteresis: `number` (defaults to 0.001)
        :param hysteresis: Absolute hysteresis around trigger

        :type auto_sensitivity: `boolean`
        :param auto_sensitivity: Configure auto or manual hysteresis for noise rejection.

        :type noise_reject: `boolean`
        :param noise_reject: Configure the Oscilloscope with a small amount of hysteresis to prevent repeated triggering due to noise # noqa

        :type hf_reject: `boolean`
        :param hf_reject: Configure the trigger signal to pass through a low pass filter to smooths out the noise # noqa

        :type source: `string` ['ChannelA', 'ChannelB', 'ChannelC', 'ChannelD', 'Input1', 'Input2', 'Input3', 'Input4', 'Output1', 'Output2', 'Output3', 'Output4', 'External'] # noqa
        :param source: Trigger Source

        """
        operation = "set_trigger"
        params = dict(
            strict=strict,
            type=type,
            level=level,
            level_low=level_low,
            level_high=level_high,
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

    def osc_measurement(self, t1, t2, trigger_source, edge, level, strict=True):
        """
        osc_measurement.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type t1: `number`
        :param t1: Time from the trigger point to the left of screen

        :type t2: `number`
        :param t2: Time from the trigger point to the right of screen. (Must be a positive number, i.e. after the trigger event) # noqa

        :type trigger_source: `string` ['ChannelA', 'ChannelB', 'ChannelC', 'ChannelD', 'Input1', 'Input2', 'Input3', 'Input4', 'Output1', 'Output2', 'Output3', 'Output4', 'External'] # noqa
        :param trigger_source: Trigger source

        :type edge: `string` ['Rising', 'Falling', 'Both']
        :param edge: Which edge to trigger on. Only edge trigger is used with this function, pulse trigger can be enabled using set_trigger() # noqa

        :type level: `number` [-5V, 5V]
        :param level: Trigger level

        """
        operation = "osc_measurement"
        params = dict(
            strict=strict,
            t1=t1,
            t2=t2,
            trigger_source=trigger_source,
            edge=edge,
            level=level,
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

    def set_timebase(self, t1, t2, max_length=1024, frame_length=None, strict=True):
        """
        set_timebase.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type t1: `number`
        :param t1: Time from the trigger point to the left of screen. This may be negative (trigger on-screen) or positive (trigger off the left of screen). # noqa

        :type t2: `number`
        :param t2: Time from the trigger point to the right of screen. (Must be a positive number, i.e. after the trigger event) # noqa

        :type max_length: `number`
        :param max_length: Maximum length of the frame to retrieve through get_data(). The API will attempt to return a frame with as many points as possible, up to this limit. # noqa

        :type frame_length: `number`
        :param frame_length: Deprecated, use `max_length` instead which better describes the real behaviour of this parameter.

        """
        operation = "set_timebase"
        params = dict(strict=strict, t1=t1, t2=t2, max_length=max_length, frame_length=frame_length)
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

        Returns a dictionary containing the data frame and the timebase. The length of the data frame
        defaults to 1024 points but can be changed using the set_timebase() function. Changes to the
        requested frame length are given as the maximum number of points that the user will accept,
        the actual length may be slightly less than this. The actual length may also change depending
        on the specific timebase, so it's recommended to write code that is able to handle variable
        frame lengths.

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
