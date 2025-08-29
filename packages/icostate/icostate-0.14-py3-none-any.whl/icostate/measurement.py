"""Measurement support code"""

# -- Imports ------------------------------------------------------------------

from __future__ import annotations

from icotronic.can import StreamingConfiguration, StreamingData
from icotronic.can.dataloss import calculate_dataloss_stats

# -- Classes ------------------------------------------------------------------

# pylint: disable=too-few-public-methods


class ChannelData:
    """Store measurement data for a single channel

    The data is stored in three list with the same length:

        - counters
        - timestamps
        - values

    Args:

        counters:

            Message counter (0 – 255) for each measured value

        timestamps:

            Timestamps for each measured value

        values:

            The measured values

    """

    def __init__(
        self,
        counters: list[float] | None = None,
        timestamps: list[float] | None = None,
        values: list[float] | None = None,
    ) -> None:
        self.counters = [] if counters is None else counters
        self.timestamps = [] if timestamps is None else timestamps
        self.values = [] if values is None else values

    def __repr__(self) -> str:
        """Get the string representation of the data

        Examples:

            Get string representation of some example data

            >>> t1 = 1756124450.256398
            >>> t2 = 1756124450.2564
            >>> data = ChannelData(counters = [1, 1, 1, 2, 2, 2],
            ...                    timestamps = [t1, t1, t1, t2, t2, t2],
            ...                    values = [4, 5, 6, 7, 8, 9])

            >>> data # doctest:+NORMALIZE_WHITESPACE
            4@1756124450.256398 #1
            5@1756124450.256398 #1
            6@1756124450.256398 #1
            7@1756124450.2564 #2
            8@1756124450.2564 #2
            9@1756124450.2564 #2

        """

        return "\n".join([
            f"{value}@{timestamp} #{counter}"
            for counter, timestamp, value in zip(
                self.counters, self.timestamps, self.values
            )
        ])


# pylint: enable=too-few-public-methods


class MeasurementData:
    """Measurement data

    Args:

        configuration:

            The streaming configuration that was is used to collect the
            measurement data

    """

    def __init__(self, configuration: StreamingConfiguration) -> None:
        self.configuration = configuration
        self.streaming_data_list: list[StreamingData] = []

    def __repr__(self) -> str:
        """Get the textual representation of the measurement data

        Returns:

            The textual representation of the measurement data

        Examples:

            >>> config = StreamingConfiguration(first=True, second=True,
            ...                                 third=False)
            >>> data = MeasurementData(config)
            >>> s1 = StreamingData(values=[1, 2], counter=255,
            ...                    timestamp=1756125747.528234)
            >>> s2 = StreamingData(values=[3, 4], counter=0,
            ...                    timestamp=1756125747.528237)
            >>> data.append(s1)

            >>> data
            Channel 1 enabled, Channel 2 enabled, Channel 3 disabled
            [1, 2]@1756125747.528234 #255

            >>> data.append(s2)
            >>> data
            Channel 1 enabled, Channel 2 enabled, Channel 3 disabled
            [1, 2]@1756125747.528234 #255
            [3, 4]@1756125747.528237 #0

        """

        return (
            f"{self.configuration}"
            + ("\n" if self.streaming_data_list else "")
            + "\n".join([
                str(streaming_data)
                for streaming_data in self.streaming_data_list
            ])
        )

    def __len__(self) -> int:
        """Get the length of the measurement data

        The length is defined as the number of streaming data items contained
        in the measurement data.

        Returns:

            The number of streaming data elements in the measurement data

        Examples:

            >>> config = StreamingConfiguration(first=True, second=True,
            ...                                 third=False)
            >>> data = MeasurementData(config)
            >>> len(data)
            0

            >>> s1 = StreamingData(values=[1, 2], counter=255,
            ...                    timestamp=1756125747.528234)
            >>> data.append(s1)
            >>> len(data)
            1

            >>> s2 = StreamingData(values=[3, 4], counter=0,
            ...                    timestamp=1756125747.528237)
            >>> data.append(s2)
            >>> len(data)
            2

        """

        return len(self.streaming_data_list)

    def first(self) -> ChannelData:
        """Get all data of the first measurement channel

        Returns:

            Data values for the first measurement channel

        Examples:

            Get first channel data of measurement with two enabled channels

            >>> config = StreamingConfiguration(first=True, second=True,
            ...                                 third=False)
            >>> data = MeasurementData(config)
            >>> s1 = StreamingData(values=[1, 2], counter=255,
            ...                    timestamp=1756125747.528234)
            >>> s2 = StreamingData(values=[3, 4], counter=0,
            ...                    timestamp=1756125747.528237)
            >>> data.append(s1)
            >>> data.append(s2)
            >>> data.first() # doctest:+NORMALIZE_WHITESPACE
            1@1756125747.528234 #255
            3@1756125747.528237 #0
            >>> data.second() # doctest:+NORMALIZE_WHITESPACE
            2@1756125747.528234 #255
            4@1756125747.528237 #0
            >>> data.third()
            <BLANKLINE>

            Get first channel data of measurement with one enabled channel

            >>> config = StreamingConfiguration(first=True, second=False,
            ...                                 third=False)
            >>> data = MeasurementData(config)
            >>> s1 = StreamingData(values=[1, 2, 3], counter=10,
            ...                    timestamp=1756126628.820695)
            >>> s2 = StreamingData(values=[4, 5, 6], counter=20,
            ...                    timestamp=1756126628.8207)
            >>> data.append(s1)
            >>> data.append(s2)
            >>> data.first() # doctest:+NORMALIZE_WHITESPACE
            1@1756126628.820695 #10
            2@1756126628.820695 #10
            3@1756126628.820695 #10
            4@1756126628.8207 #20
            5@1756126628.8207 #20
            6@1756126628.8207 #20
            >>> data.second()
            <BLANKLINE>
            >>> data.third()
            <BLANKLINE>

        """

        channel_data = ChannelData()
        configuration = self.configuration

        if configuration.first:
            if not configuration.second and not configuration.third:
                # Three values
                for streaming_data in self.streaming_data_list:
                    for _ in range(3):
                        channel_data.counters.append(streaming_data.counter)
                        channel_data.timestamps.append(
                            streaming_data.timestamp
                        )
                    channel_data.values.extend(streaming_data.values)
            else:
                # One value
                for streaming_data in self.streaming_data_list:
                    channel_data.counters.append(streaming_data.counter)
                    channel_data.timestamps.append(streaming_data.timestamp)
                    channel_data.values.append(streaming_data.values[0])

        return channel_data

    def second(self) -> ChannelData:
        """Get all data of the second measurement channel

        Returns:

            Data values for the second measurement channel

        Examples:

            Get second channel data of measurement with two enabled channels

            >>> config = StreamingConfiguration(first=False, second=True,
            ...                                 third=True)
            >>> data = MeasurementData(config)
            >>> s1 = StreamingData(values=[1, 2], counter=255,
            ...                    timestamp=1756125747.528234)
            >>> s2 = StreamingData(values=[3, 4], counter=0,
            ...                    timestamp=1756125747.528237)
            >>> data.append(s1)
            >>> data.append(s2)
            >>> data.first()
            <BLANKLINE>
            >>> data.second() # doctest:+NORMALIZE_WHITESPACE
            1@1756125747.528234 #255
            3@1756125747.528237 #0
            >>> data.third() # doctest:+NORMALIZE_WHITESPACE
            2@1756125747.528234 #255
            4@1756125747.528237 #0

            Get second channel data of measurement with one enabled channel

            >>> config = StreamingConfiguration(first=False, second=True,
            ...                                 third=False)
            >>> data = MeasurementData(config)
            >>> s1 = StreamingData(values=[1, 2, 3], counter=10,
            ...                    timestamp=1756126628.820695)
            >>> s2 = StreamingData(values=[4, 5, 6], counter=20,
            ...                    timestamp=1756126628.8207)
            >>> data.append(s1)
            >>> data.append(s2)
            >>> data.first()
            <BLANKLINE>
            >>> data.second() # doctest:+NORMALIZE_WHITESPACE
            1@1756126628.820695 #10
            2@1756126628.820695 #10
            3@1756126628.820695 #10
            4@1756126628.8207 #20
            5@1756126628.8207 #20
            6@1756126628.8207 #20
            >>> data.third()
            <BLANKLINE>

        """

        channel_data = ChannelData()
        configuration = self.configuration

        if configuration.second:
            if not configuration.first and not configuration.third:
                # Three values
                for streaming_data in self.streaming_data_list:
                    for _ in range(3):
                        channel_data.counters.append(streaming_data.counter)
                        channel_data.timestamps.append(
                            streaming_data.timestamp
                        )
                    channel_data.values.extend(streaming_data.values)
            else:
                # One value
                for streaming_data in self.streaming_data_list:
                    channel_data.counters.append(streaming_data.counter)
                    channel_data.timestamps.append(streaming_data.timestamp)
                    channel_data.values.append(
                        streaming_data.values[0]
                        if not configuration.first
                        else streaming_data.values[1]
                    )

        return channel_data

    def third(self) -> ChannelData:
        """Get all data of the third measurement channel

        Returns:

            Data values for the third measurement channel

        Examples:

            Get third channel data of measurement with two enabled channels

            >>> config = StreamingConfiguration(first=True, second=False,
            ...                                 third=True)
            >>> data = MeasurementData(config)
            >>> s1 = StreamingData(values=[1, 2], counter=255,
            ...                    timestamp=1756125747.528234)
            >>> s2 = StreamingData(values=[3, 4], counter=0,
            ...                    timestamp=1756125747.528237)
            >>> data.append(s1)
            >>> data.append(s2)
            >>> data.first() # doctest:+NORMALIZE_WHITESPACE
            1@1756125747.528234 #255
            3@1756125747.528237 #0
            >>> data.second()
            <BLANKLINE>
            >>> data.third() # doctest:+NORMALIZE_WHITESPACE
            2@1756125747.528234 #255
            4@1756125747.528237 #0

            Get third channel data of measurement with one enabled channel

            >>> config = StreamingConfiguration(first=False, second=False,
            ...                                 third=True)
            >>> data = MeasurementData(config)
            >>> s1 = StreamingData(values=[1, 2, 3], counter=10,
            ...                    timestamp=1756126628.820695)
            >>> s2 = StreamingData(values=[4, 5, 6], counter=20,
            ...                    timestamp=1756126628.8207)
            >>> data.append(s1)
            >>> data.append(s2)
            >>> data.first()
            <BLANKLINE>
            >>> data.second()
            <BLANKLINE>
            >>> data.third() # doctest:+NORMALIZE_WHITESPACE
            1@1756126628.820695 #10
            2@1756126628.820695 #10
            3@1756126628.820695 #10
            4@1756126628.8207 #20
            5@1756126628.8207 #20
            6@1756126628.8207 #20

        """

        channel_data = ChannelData()
        configuration = self.configuration

        if configuration.third:
            if not configuration.first and not configuration.second:
                # Three values
                for streaming_data in self.streaming_data_list:
                    for _ in range(3):
                        channel_data.counters.append(streaming_data.counter)
                        channel_data.timestamps.append(
                            streaming_data.timestamp
                        )
                    channel_data.values.extend(streaming_data.values)
            else:
                # One value
                for streaming_data in self.streaming_data_list:
                    channel_data.counters.append(streaming_data.counter)
                    channel_data.timestamps.append(streaming_data.timestamp)
                    channel_data.values.append(streaming_data.values[-1])

        return channel_data

    def dataloss(self) -> float:
        """Get measurement dataloss based on message counters

        Returns:

            The overall amount of dataloss as number between 0 (no data loss)
            and 1 (all data lost).

        """

        return calculate_dataloss_stats((
            streaming_data.counter
            for streaming_data in self.streaming_data_list
        )).dataloss()

    def append(self, data: StreamingData) -> None:
        """Append some streaming data to the measurement

        Args:

            data:

                The streaming data that should be added to the measurement

        Examples:

            Append some streaming data to a measurement

            >>> config = StreamingConfiguration(first=True, second=True,
            ...                                 third=True)
            >>> data = MeasurementData(config)
            >>> data
            Channel 1 enabled, Channel 2 enabled, Channel 3 enabled

            >>> s1 = StreamingData(values=[4, 5, 3], counter=15,
            ...                    timestamp=1756197008.776551)
            >>> data.append(s1)
            >>> data
            Channel 1 enabled, Channel 2 enabled, Channel 3 enabled
            [4, 5, 3]@1756197008.776551 #15

        """

        self.streaming_data_list.append(data)

    def extend(self, data: MeasurementData) -> None:
        """Extend this measurement data with some other measurement data

        Args:

            data:

                The measurement data that should be added to this measurement

        Examples:

            Extend measurement data with other measurement data

            >>> config = StreamingConfiguration(first=True, second=False,
            ...                                 third=True)
            >>> data1 = MeasurementData(config)
            >>> s1 = StreamingData(values=[1, 2], counter=255,
            ...                    timestamp=1756125747.528234)
            >>> s2 = StreamingData(values=[3, 4], counter=0,
            ...                    timestamp=1756125747.528237)
            >>> data1.append(s1)
            >>> data1.append(s2)
            >>> data1
            Channel 1 enabled, Channel 2 disabled, Channel 3 enabled
            [1, 2]@1756125747.528234 #255
            [3, 4]@1756125747.528237 #0

            >>> data2 = MeasurementData(config)
            >>> s3 = StreamingData(values=[10, 20], counter=1,
            ...                    timestamp=1756125747.678912)
            >>> data2.append(s3)
            >>> data2
            Channel 1 enabled, Channel 2 disabled, Channel 3 enabled
            [10, 20]@1756125747.678912 #1

            >>> data1.extend(data2)
            >>> data1
            Channel 1 enabled, Channel 2 disabled, Channel 3 enabled
            [1, 2]@1756125747.528234 #255
            [3, 4]@1756125747.528237 #0
            [10, 20]@1756125747.678912 #1

        """

        if self.configuration != data.configuration:
            raise ValueError(
                f"Trying to merge measurement data {self.configuration} with "
                "different streaming configuration: {data.configuration}"
            )

        self.streaming_data_list.extend(data.streaming_data_list)


if __name__ == "__main__":
    from doctest import testmod

    testmod()
