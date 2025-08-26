from moku import Moku, MultiInstrumentSlottable


class FrequencyResponseAnalyzer(MultiInstrumentSlottable, Moku):
    """
    FrequencyResponseAnalyzer instrument object.

    This instrument measures the transfer function of a
    system by generating a swept sine wave and measuring
    the system response on the input

    Read more at https://apis.liquidinstruments.com/reference/fra

    """

    INSTRUMENT_ID = 9
    OPERATION_GROUP = "fra"

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

    def fra_measurement(
        self,
        channel,
        mode="InOut",
        start_frequency=0,
        stop_frequency=0,
        averaging_duration=0,
        averaging_cycles=0,
        output_amplitude=0,
        strict=True,
    ):
        """
        fra_measurement.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type mode: `string` ['In', 'InOut', 'InIn1']
        :param mode: FRA Measurement mode

        :type start_frequency: `number` [1e-3Hz, 20e6Hz]  (defaults to 0)
        :param start_frequency: Sweep start frequency

        :type stop_frequency: `number` [1e-3Hz, 20e6Hz]  (defaults to 0)
        :param stop_frequency: Sweep end frequency

        :type averaging_duration: `number` [1e-6Sec, 10Sec]  (defaults to 0)
        :param averaging_duration: Minimum averaging time per sweep point.

        :type averaging_cycles: `integer` [1, 1048576]  (defaults to 0)
        :param averaging_cycles: Minimum averaging cycles per sweep point.

        :type output_amplitude: `number` [2e-3Vpp, 10Vpp]  (defaults to 0)
        :param output_amplitude: Output amplitude

        """
        operation = "fra_measurement"
        params = dict(
            strict=strict,
            channel=channel,
            mode=mode,
            start_frequency=start_frequency,
            stop_frequency=stop_frequency,
            averaging_duration=averaging_duration,
            averaging_cycles=averaging_cycles,
            output_amplitude=output_amplitude,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def measurement_mode(self, mode="InOut", strict=True):
        """
        measurement_mode.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type mode: `string` ['In', 'InOut', 'InIn1']
        :param mode: FRA Measurement mode

        """
        operation = "measurement_mode"
        params = dict(
            strict=strict,
            mode=mode,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_sweep(
        self,
        start_frequency=0,
        stop_frequency=0,
        num_points=512,
        averaging_time=0,
        averaging_cycles=0,
        settling_time=0,
        settling_cycles=0,
        dynamic_amplitude=False,
        linear_scale=False,
        strict=True,
    ):
        """
        set_sweep.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type start_frequency: `number` [1e-3Hz, 20e6Hz]  (defaults to 0)
        :param start_frequency: Sweep start frequency

        :type stop_frequency: `number` [1e-3Hz, 20e6Hz]  (defaults to 0)
        :param stop_frequency: Sweep stop frequency

        :type num_points: `integer`
        :param num_points: Number of points in the sweep (rounded to nearest power of 2) # noqa

        :type averaging_time: `number` [1e-6Sec, 10Sec]  (defaults to 0)
        :param averaging_time: Minimum averaging time per sweep point.

        :type averaging_cycles: `integer` [1, 1048576]  (defaults to 0)
        :param averaging_cycles: Minimum averaging cycles per sweep point.

        :type settling_time: `number` [1e-6Sec, 10Sec]  (defaults to 0)
        :param settling_time: Minimum settling time per sweep point.

        :type settling_cycles: `integer` [1, 1048576]  (defaults to 0)
        :param settling_cycles: Minimum settling cycles per sweep point.

        :type linear_scale: `boolean`
        :param linear_scale: Enables linear scale. If set to false scale is set to logarithmic. Defaults to false # noqa

        """
        operation = "set_sweep"
        params = dict(
            strict=strict,
            start_frequency=start_frequency,
            stop_frequency=stop_frequency,
            num_points=num_points,
            averaging_time=averaging_time,
            averaging_cycles=averaging_cycles,
            settling_time=settling_time,
            settling_cycles=settling_cycles,
            dynamic_amplitude=dynamic_amplitude,
            linear_scale=linear_scale,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_sweep(self):
        """
        get_sweep.
        """
        operation = "get_sweep"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def start_sweep(self, single=False, strict=True):
        """
        start_sweep.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type single: `boolean`
        :param single: Enable single sweep (otherwise loop).

        """
        operation = "start_sweep"
        params = dict(
            strict=strict,
            single=single,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def stop_sweep(self):
        """
        stop_sweep.
        """
        operation = "stop_sweep"
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation)

    def set_output(
        self,
        channel,
        amplitude,
        offset=0,
        enable_amplitude=True,
        enable_offset=True,
        strict=True,
    ):
        """
        set_output.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type amplitude: `number` [-5V, 5V]
        :param amplitude: Waveform peak-to-peak amplitude

        :type offset: `number` [-5V, 5V]  (defaults to 0)
        :param offset: DC offset applied to the waveform

        :type enable_amplitude: `bool`(defaults to True)
        :param enable_amplitude: Enable amplitude on the given channel

        :type enable_offset: `bool`(defaults to True)
        :param enable_offset: Enable offset on the given channel

        """
        operation = "set_output"
        params = dict(
            strict=strict,
            channel=channel,
            amplitude=amplitude,
            offset=offset,
            enable_amplitude=enable_amplitude,
            enable_offset=enable_offset,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

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
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

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

    def set_output_phase(self, channel, phase, strict=True):
        """
        set_output_phase.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type phase: `number`
        :param phase: Output phase

        """
        operation = "set_output_phase"
        params = dict(
            strict=strict,
            channel=channel,
            phase=phase,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_harmonic_multiplier(self, multiplier=1, strict=True):
        """
        set_harmonic_multiplier.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type multiplier: `integer` [1, 15]  (defaults to 1)
        :param multiplier: Multiplier applied to the fundamental frequency

        """
        operation = "set_harmonic_multiplier"
        params = dict(
            strict=strict,
            multiplier=multiplier,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_harmonic_multiplier(self):
        """
        get_harmonic_multiplier.
        """
        operation = "get_harmonic_multiplier"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

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

    def get_data(self, timeout=60, wait_reacquire=False, wait_complete=False):
        """
        get_data.

        :type timeout: `number` Seconds (defaults to 60)
        :param timeout: Wait for n seconds to receive a data frame

        :type wait_reacquire: `boolean`
        :param wait_reacquire: Wait until the data is reacquired

        :type wait_complete: `boolean`
        :param wait_complete: Wait until entire frame is available


        .. important::
            Default timeout for reading the data is 10 seconds. It
            can be increased by setting the read_timeout property of
            session object.

            Example: ``i.session.read_timeout=100`` (in seconds)

        """
        operation = "get_data"
        params = dict(
            timeout=timeout, wait_reacquire=wait_reacquire, wait_complete=wait_complete
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )
