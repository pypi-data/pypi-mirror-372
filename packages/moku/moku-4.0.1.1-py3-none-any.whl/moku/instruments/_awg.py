from moku import Moku, MultiInstrumentSlottable


class ArbitraryWaveformGenerator(MultiInstrumentSlottable, Moku):
    """
    Arbitrary Waveform Generator instrument object.

    The Arbitrary Waveform Generator takes a time-series of
     voltage values, and generates the corresponding
     waveform at the DACs at a configurable rate.

    Read more at https://apis.liquidinstruments.com/reference/awg

    """

    INSTRUMENT_ID = 15
    OPERATION_GROUP = "awg"

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

    def enable_output(self, channel, enable=True, strict=True):
        """
        enable_output.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type enable: `boolean`
        :param enable: Enable the specified output channel

        """
        operation = "enable_output"
        params = dict(
            strict=strict,
            channel=channel,
            enable=enable,
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

    def generate_waveform(
        self,
        channel,
        sample_rate,
        lut_data=None,
        frequency=None,
        amplitude=None,
        phase=0,
        offset=0,
        interpolation=False,
        strict=True,
    ):
        """
        generate_waveform.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type sample_rate: `string` ['Auto', '1.25Gs', '1Gs', '625Ms', '500Ms', '312.5Ms', '250Ms', '125Ms', '62.5Ms', '31.25Ms', '15.625Ms'] # noqa
        :param sample_rate: Defines the output sample rate of the AWG. If you do not specify a mode, the fastest output rate for the given data length will be automatically chosen. This is correct in almost all circumstances. # noqa

        :type lut_data: `list`
        :param lut_data: Lookup table coefficients, each coefficient should be in the range of [-1.0, 1.0] # noqa
        :type frequency: `number` [1e-3Hz, 10e6Hz]
        :param frequency: Frequency of the waveform

        :type amplitude: `number` [4e-3V, 10V]
        :param amplitude: Waveform peak-to-peak amplitude

        :type phase: `number` [0Deg, 360Deg]  (defaults to 0)
        :param phase: Waveform phase offset

        :type offset: `number` [-5V, 5V]  (defaults to 0)
        :param offset: DC offset applied to the waveform

        :type interpolation: `boolean`  (defaults to False)
        :param interpolation: Enable linear interpolation of LUT entries.

        """
        operation = "generate_waveform"
        params = dict(
            strict=strict,
            channel=channel,
            sample_rate=sample_rate,
            lut_data=lut_data,
            frequency=frequency,
            amplitude=amplitude,
            phase=phase,
            offset=offset,
            interpolation=interpolation,
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

    def pulse_modulate(self, channel, dead_cycles=10, dead_voltage=0, strict=True):
        """
        pulse_modulate.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type dead_cycles: `integer` [1, 262144]  (defaults to 10)
        :param dead_cycles: Number of cycles which show the dead voltage.

        :type dead_voltage: `number` [-5V, 5V]  (defaults to 0)
        :param dead_voltage: Signal level during dead time

        """
        operation = "pulse_modulate"
        params = dict(
            strict=strict,
            channel=channel,
            dead_cycles=dead_cycles,
            dead_voltage=dead_voltage,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def burst_modulate(
        self,
        channel,
        trigger_source,
        trigger_mode,
        burst_cycles=1,
        trigger_level=0,
        input_range=None,
        strict=True,
    ):
        """
        burst_modulate.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type trigger_source: `string` ['Input1', 'Input2', 'Input3', 'Input4', 'InputA', 'InputB', 'InputC', 'InputD', 'External'] # noqa
        :param trigger_source: Trigger source # noqa

        :type trigger_mode: `string` ['Start', 'NCycle']
        :param trigger_mode: Burst mode

        :type burst_cycles: `number` [1, 1e6]  (defaults to 1)
        :param burst_cycles: Number of cycles to generate when triggered

        :type trigger_level: `number` [-5V, 5V]  (defaults to 0)
        :param trigger_level: Trigger level

        :type input_range: `string` ['400mVpp', '1Vpp', '4Vpp', '10Vpp', '40Vpp', '50Vpp']
        :param input_range: Input Range

        """
        operation = "burst_modulate"
        params = dict(
            strict=strict,
            channel=channel,
            trigger_source=trigger_source,
            trigger_mode=trigger_mode,
            burst_cycles=burst_cycles,
            trigger_level=trigger_level,
            input_range=input_range,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def manual_trigger(self):
        """
        Trigger all channels that are configured for manual triggering.
        """
        operation = "manual_trigger"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation
        )
