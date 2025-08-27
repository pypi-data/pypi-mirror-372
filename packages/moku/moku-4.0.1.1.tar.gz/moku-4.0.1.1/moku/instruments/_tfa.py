from moku import Moku, MultiInstrumentSlottable


class TimeFrequencyAnalyzer(MultiInstrumentSlottable, Moku):
    """
    Measure intervals between configurable start and stop events
    with sub-ns precision, compute histograms of interval duration
    losslessly and in real-time, and save high-resolution event
    timestamps to a file.

    Read more at https://apis.liquidinstruments.com/reference/tfa

    """

    INSTRUMENT_ID = 11
    OPERATION_GROUP = "tfa"

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
        return cls(slot=slot, multi_instrument=multi_instrument)

    def set_defaults(self):
        """
        set_defaults
        """
        operation = "set_defaults"
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation)

    def set_frontend(self, channel, impedance, coupling, range, strict=True):
        """
        set_frontend
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
        get_frontend
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

    def set_interpolation(self, mode="Linear", strict=True):
        """
        set_interpolation
        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type mode: `string` ['None', 'Linear']
        :param mode: Interpolation mode

        """
        operation = "set_interpolation"
        params = dict(
            strict=strict,
            mode=mode,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_interpolation(self):
        """
        get_interpolation
        """
        operation = "get_interpolation"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def set_acquisition_mode(
        self,
        mode="Continuous",
        gate_source=None,
        gate_threshold=None,
        window_length=None,
        strict=True,
    ):
        """
        set_acquisition_mode
        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type mode: `string` ['Continuous', 'Windowed', 'Gated']
        :param mode: Acquisition mode

        :type gate_source: `string` ['ChannelA', 'ChannelB', 'ChannelC', 'ChannelD', 'Input1', 'Input2', 'Input3', 'Input4', 'Output1', 'Output2', 'Output3', 'Output4', 'External'] # noqa
        :param gate_source: Acquisition channel

        :type gate_threshold: `number`
        :param gate_threshold: Acquition threshold

        :type window_length: `number`
        :param window_length: Window length

        """
        operation = "set_acquisition_mode"
        params = dict(
            strict=strict,
            mode=mode,
            gate_source=gate_source,
            gate_threshold=gate_threshold,
            window_length=window_length,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_acquisition_mode(self):
        """
        get_acquisition_mode
        """
        operation = "get_acquisition_mode"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)

    def set_histogram(self, start_time, stop_time, strict=True):
        """
        set_histogram
        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type start_time: `number`
        :param start_time: Start time

        :type stop_time: `number`
        :param stop_time: Stop time

        """
        operation = "set_histogram"
        params = dict(
            strict=strict,
            start_time=start_time,
            stop_time=stop_time,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_event_detector(self, id, source, threshold=0, edge="Rising", holdoff=0.0, strict=True):
        """
        set_event_detector
        :type id: `integer`
        :param id: The numerical id of the event

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type source: `string` ['ChannelA', 'ChannelB', 'ChannelC', 'ChannelD', 'Input1', 'Input2', 'Input3', 'Input4', 'Output1', 'Output2', 'Output3', 'Output4', 'External'] # noqa
        :param source: Source

        :type threshold: `number`
        :param threshold: Threshold

        :type edge: `string` ['Rising', 'Falling', 'Both']
        :param edge: Detection edge

        :type holdoff: `number`
        :param holdoff: Holdoff time

        """
        operation = "set_event_detector"
        params = dict(
            id=id,
            strict=strict,
            source=source,
            threshold=threshold,
            edge=edge,
            holdoff=holdoff
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_event_detector(self, id):
        """
        get_event_detector
        :type id: `integer`
        :param id: The numerical id of the event

        """
        operation = "get_event_detector"
        params = dict(
            id=id,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def set_interval_analyzer(
        self, id, start_event_id, stop_event_id, enable=True, strict=True
    ):
        """
        set_interval_analyzer
        :type id: `integer`
        :param id: The numerical id of the interval analyzer

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type enable: `boolean`
        :param enable: Enable/disable interval analyzer

        :type start_event_id: `integer`
        :param start_event_id: Start event

        :type stop_event_id: `integer`
        :param stop_event_id: Stop event

        """
        operation = "set_interval_analyzer"
        params = dict(
            id=id,
            strict=strict,
            enable=enable,
            start_event_id=start_event_id,
            stop_event_id=stop_event_id,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def get_interval_analyzer(self, id):
        """
        get_interval_analyzer
        :type id: `integer`
        :param id: The numerical id of the interval analyzer

        """
        operation = "get_interval_analyzer"
        params = dict(
            id=id,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def generate_output(
        self,
        channel,
        signal_type,
        scaling,
        zero_point=0,
        output_range=None,
        invert=False,
        strict=True,
    ):
        """
        generate_output
        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type signal_type: `string` ['Interval', 'Count']
        :param signal_type: Output signal type

        :type scaling: `number`
        :param scaling: Scaling factor

        :type zero_point: `number`
        :param zero_point: Zero point

        :type output_range: `string` ['2Vpp', '10Vpp']
        :param output_range: Output range

        :type invert: `boolean`
        :param invert: Whether to invert the output signal

        """
        operation = "generate_output"
        params = dict(
            strict=strict,
            channel=channel,
            signal_type=signal_type,
            scaling=scaling,
            zero_point=zero_point,
            output_range=output_range,
            invert=invert,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def disable_output(self, channel, strict=True):
        """
        disable_output
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

    def start_logging(
        self,
        event_ids,
        duration=60,
        file_name_prefix="",
        comments="",
        delay=0,
        quantity="EventTimestamp",
        strict=True,
    ):
        """
        start_logging
        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type duration: `number` Sec (defaults to 60)
        :param duration: Duration to log for

        :type file_name_prefix: `string`
        :param file_name_prefix: Optional file name prefix

        :type comments: `string`
        :param comments: Optional comments to be included

        :type delay: `integer` Sec (defaults to 0)
        :param delay: Delay the start by

        :type event_ids: `list`
        :param event_ids: List of event IDs to log (starting from 1)

        :type quantity: `string` ['EventTimestamp']
        :param quantity: The quantity to log (currently only event timestamp is supported) # noqa

        """
        operation = "start_logging"
        params = dict(
            strict=strict,
            duration=duration,
            file_name_prefix=file_name_prefix,
            comments=comments,
            delay=delay,
            event_ids=event_ids,
            quantity=quantity,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def stop_logging(self):
        """
        stop_logging
        """
        operation = "stop_logging"
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation)

    def logging_progress(self):
        """
        logging_progress
        """
        operation = "logging_progress"
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation)

    def get_data(self, timeout=60, strict=True):
        """
        get_data
        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type timeout: `number`
        :param timeout: How long to wait for data to be acquired


        .. important::
            Default timeout for reading the data is 10 seconds. It
            can be increased by setting the read_timeout property of
            session object.

            Example: ``i.session.read_timeout=100`` (in seconds)

        """
        operation = "get_data"
        params = dict(
            strict=strict,
            timeout=timeout,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation, params
        )

    def clear_data(self):
        """
        clear_data
        """
        operation = "clear_data"
        return self.session.post(f"slot{self.slot}/{self.operation_group}", operation)

    def summary(self):
        """
        summary
        """
        operation = "summary"
        return self.session.get(f"slot{self.slot}/{self.operation_group}", operation)
