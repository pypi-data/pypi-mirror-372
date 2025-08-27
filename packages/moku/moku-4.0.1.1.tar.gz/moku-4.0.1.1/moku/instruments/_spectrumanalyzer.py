from moku import Moku, MultiInstrumentSlottable


class SpectrumAnalyzer(MultiInstrumentSlottable, Moku):
    """
    Spectrum Analyzer instrument object.

    Spectrum Analyzer provides frequency-domain analysis of
    input signals. It features switchable window functions,
    resolution bandwidth, averaging modes and more.

    Read more at https://apis.liquidinstruments.com/reference/specan

    """

    INSTRUMENT_ID = 2
    OPERATION_GROUP = "spectrumanalyzer"

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
            f"slot{self.slot}/{self.operation_group}", operation, params=params
        )  # noqa

    def sa_output(self, channel, amplitude, frequency, strict=True):
        """
        sa_output.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type amplitude: `number`
        :param amplitude: Waveform peak-to-peak amplitude

        :type frequency: `number` [0Hz, 30e6Hz]
        :param frequency: Frequency of the wave

        """
        operation = "sa_output"
        params = dict(
            strict=strict,
            channel=channel,
            amplitude=amplitude,
            frequency=frequency,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_rbw(self):
        """
        get_rbw.
        """
        operation = "get_rbw"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def set_rbw(self, mode, rbw_value=5000, strict=True):
        """
        set_rbw.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type mode: `string` ['Auto', 'Manual', 'Minimum']
        :param mode: Desired resolution bandwidth (Hz)

        :type rbw_value: `number`
        :param rbw_value: RBW value (only in manual mode)

        """
        operation = "set_rbw"
        params = dict(
            strict=strict,
            mode=mode,
            rbw_value=rbw_value,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_span(self):
        """
        get_span.
        """
        operation = "get_span"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def set_span(self, frequency1, frequency2, strict=True):
        """
        set_span.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type frequency1: `number` [0Hz, 30e6Hz]
        :param frequency1: Left-most frequency

        :type frequency2: `number` [0Hz, 30e6Hz]
        :param frequency2: Right-most frequency

        """
        operation = "set_span"
        params = dict(
            strict=strict,
            frequency1=frequency1,
            frequency2=frequency2,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def sa_measurement(
        self,
        channel,
        frequency1,
        frequency2,
        rbw="Auto",
        rbw_value=5000,
        window="BlackmanHarris",
        strict=True,
    ):
        """
        sa_measurement.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type frequency1: `number` [0Hz, 30e6Hz]
        :param frequency1: Left-most frequency

        :type frequency2: `number` [0Hz, 30e6Hz]
        :param frequency2: Right-most frequency

        :type rbw: `string` ['Auto', 'Manual', 'Minimum']
        :param rbw: Desired resolution bandwidth (Hz)

        :type rbw_value: `number`
        :param rbw_value: RBW value (only in manual mode)

        :type window: `string` ['BlackmanHarris', 'FlatTop', 'Rectangular', 'Bartlett', 'Hamming', 'Hann', 'Nuttall', 'Gaussian', 'Kaiser'] # noqa
        :param window: Window Function

        """
        operation = "sa_measurement"
        params = dict(
            strict=strict,
            channel=channel,
            frequency1=frequency1,
            frequency2=frequency2,
            rbw=rbw,
            rbw_value=rbw_value,
            window=window,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_window(self, window, strict=True):
        """
        set_window.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type window: `string` ['BlackmanHarris', 'FlatTop', 'Rectangular', 'Bartlett', 'Hamming', 'Hann', 'Nuttall', 'Gaussian', 'Kaiser'] # noqa
        :param window: Window Function

        """
        operation = "set_window"
        params = dict(
            strict=strict,
            window=window,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_window(self):
        """
        get_window.
        """
        operation = "get_window"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

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

    def set_averaging(self, target_duration=0.1, strict=True):
        """
        set_averaging

        :type target_duration: `boolean`
        :param target_duration: Average frames for the given duration.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        """
        operation = "set_averaging"
        params = dict(target_duration=target_duration, strict=strict)
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def enable_xcorr(self, channel_a, channel_b, strict=True):
        """
        enable_xcorr

        :type channel_a: `string` ['Input1', 'Input2', 'Input3', 'Input4', 'InputA', 'InputB', 'InputC', 'InputD'] # noqa
        :param channel_a: First channel to cross correlate

        :type channel_b: `string` ['Input1', 'Input2', 'Input3', 'Input4', 'InputA', 'InputB', 'InputC', 'InputD'] # noqa
        :param channel_b: Second channel to cross correlate

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        """
        operation = "enable_xcorr"
        params = dict(channel_a=channel_a, channel_b=channel_b, strict=strict)
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def disable_xcorr(self):
        """
        disable_xcorr
        """
        operation = "disable_xcorr"
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation)

    def get_data(
        self,
        timeout=60,
        wait_reacquire=False,
        wait_complete=True,
        units="dBm",
        psdUnits=False,
        measurements=False,
        strict=True,
    ):
        """
        get_data.

        :type timeout: `number` Seconds (defaults to 60)
        :param timeout: Wait for n seconds to receive a data frame

        :type wait_reacquire: `boolean`
        :param wait_reacquire: Wait until new dataframe is reacquired

        :type wait_complete: `boolean`
        :param wait_complete: Wait until entire frame is available

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type units: `string` ['dBm', 'Vrms', 'Vpp', 'dBV']
        :param units: Units

        :type psdUnits: `boolean`
        :param psdUnits: PSD Units

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
            strict=strict,
            units=units,
            psdUnits=psdUnits,
            measurements=measurements,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )
