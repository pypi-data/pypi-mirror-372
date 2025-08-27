from moku import Moku, MultiInstrumentSlottable


class WaveformGenerator(MultiInstrumentSlottable, Moku):
    """
    Waveform Generator instrument object.

    Supports the generation of Sine, Square and Ramp waves.

     - The output waveforms can also be frequency, phase or
       amplitude modulated.
     - The modulation source can be another
       internally-generated Sinewave, the associated analog
       input channel or the other output channel.
       That other output channel may itself be modulated in
       some way, allowing the creation of very complex
       waveforms

    Read more at https://apis.liquidinstruments.com/reference/waveformgenerator

    """

    INSTRUMENT_ID = 4
    OPERATION_GROUP = "waveformgenerator"

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

    def set_defaults(self):
        """
        set_defaults.
        """
        operation = "set_defaults"
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation)

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

        :type range: `string` ['100mVpp', '400mVpp' '1Vpp', '2Vpp', '4Vpp', '10Vpp', '40Vpp', '50Vpp'] # noqa
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

    def set_modulation(
        self, channel, type, source, depth=0, frequency=10000000, strict=True
    ):
        """
        set_modulation.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type type: `string` ['Amplitude', 'Frequency', 'Phase', 'PulseWidth']
        :param type: Modulation type

        :type source: `string` ['Input1', 'Input2', 'Input3', 'Input4', 'InputA', 'InputB', 'InputC', 'InputD', 'Output1', 'Output2', 'Output3', 'Output4', 'OutputA', 'OutputB', 'Internal'] # noqa
        :param source: Modulation source

        :type depth: `number`  (defaults to 0)
        :param depth: Modulation depth (depends on modulation type): Percentage modulation depth, Frequency Deviation/Volt or +/- phase shift/Volt # noqa

        :type frequency: `number` [0Hz, 50e6Hz]  (defaults to 10000000)
        :param frequency: Frequency of internally-generated sine wave modulation. This parameter is ignored if the source is set to ADC or DAC. # noqa

        """
        operation = "set_modulation"
        params = dict(
            strict=strict,
            channel=channel,
            type=type,
            source=source,
            depth=depth,
            frequency=frequency,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def disable_modulation(self, channel, strict=True):
        """
        disable_modulation.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "disable_modulation"
        params = dict(
            strict=strict,
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_burst_mode(
        self,
        channel,
        source,
        mode,
        trigger_level=0,
        burst_cycles=3,
        burst_duration=0.1,
        burst_period=1,
        input_range=None,
        strict=True,
    ):
        """
        set_burst_mode.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type source: `string` ['Input1', 'Input2', 'Input3', 'Input4', 'InputA', 'InputB', 'InputC', 'InputD', 'Output1', 'Output2', 'Output3', 'Output4', 'OutputA', 'OutputB', 'Internal', 'External'] # noqa
        :param source: Trigger source

        :type mode: `string` ['Gated', 'Start', 'NCycle']
        :param mode: Burst mode

        :type trigger_level: `number` [-5V, 5V]  (defaults to 0)
        :param trigger_level: Trigger threshold level

        :type burst_cycles: `number` [1, 1e6]  (defaults to 3)
        :param burst_cycles: The integer number of signal repetitions to generate once triggered (NCycle mode only) # noqa

        :type burst_duration: `number` [1 cycle periodSec, 1e3Sec]  (defaults to 0.1) # noqa
        :param burst_duration: Burst duration

        :type burst_period: `number`
        :param burst_period: Burst Period

        :type input_range: `string` ['400mVpp', '1Vpp', '4Vpp', '10Vpp', '40Vpp', '50Vpp'] # noqa
        :param input_range: Input Range

        """
        operation = "set_burst_mode"
        params = dict(
            strict=strict,
            channel=channel,
            source=source,
            mode=mode,
            trigger_level=trigger_level,
            burst_cycles=burst_cycles,
            burst_duration=burst_duration,
            burst_period=burst_period,
            input_range=input_range,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_sweep_mode(
        self,
        channel,
        source,
        stop_frequency=30000000,
        sweep_time=1,
        trigger_level=0,
        strict=True,
    ):
        """
        set_sweep_mode.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type source: `string` ['Input1', 'Input2', 'Input3', 'Input4', 'InputA', 'InputB', 'InputC', 'InputD', 'Output1', 'Output2', 'Output3', 'Output4', 'OutputA', 'OutputB', 'Internal', 'External'] # noqa
        :param source: Trigger source

        :type stop_frequency: `number` [100Hz, 20e6Hz]  (defaults to 30000000)
        :param stop_frequency: Sweep stop Frequency

        :type sweep_time: `number` [1 cycle periodSec, 1e3Sec]  (defaults to 1)
        :param sweep_time: Duration of sweep

        :type trigger_level: `number` [-5V, 5V]  (defaults to 0)
        :param trigger_level: Trigger threshold level

        """
        operation = "set_sweep_mode"
        params = dict(
            strict=strict,
            channel=channel,
            source=source,
            stop_frequency=stop_frequency,
            sweep_time=sweep_time,
            trigger_level=trigger_level,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def sync_phase(self):
        """
        sync_phase.
        """
        operation = "sync_phase"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def manual_trigger(self):
        """
        Trigger all channels that are configured for manual triggering.
        """
        operation = "manual_trigger"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation
        )
