"""Support for storing measurement data (in HDF5)"""

# -- Imports ------------------------------------------------------------------

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from types import TracebackType

from tables import (
    File,
    Filters,
    Float32Col,
    IsDescription,
    MetaAtom,
    MetaIsDescription,
    NoSuchNodeError,
    open_file,
    UInt8Col,
    UInt64Col,
)
from tables.exceptions import HDF5ExtError

from icotronic.can.adc import ADCConfiguration
from icotronic.can.dataloss import calculate_dataloss_stats, MessageStats
from icotronic.can.streaming import StreamingConfiguration, StreamingData

# -- Functions ----------------------------------------------------------------


def create_acceleration_description(
    attributes: dict[str, MetaAtom],
) -> MetaIsDescription:
    """Create a new ``IsDescription`` class to store acceleration data

    Args:

        attributes:
            A dictionary containing additional columns to store specific
            acceleration data. The key specifies the name of the attribute,
            while the value specifies the type.

    Examples:

        Create an example acceleration description class

        >>> description_x_acceleration = create_acceleration_description(
        ...     dict(x=Float32Col()))
        >>> list(description_x_acceleration.columns.keys())
        ['counter', 'timestamp', 'x']

    """

    description_class = type(
        "ExtendedAccelerationDescription",
        (AccelerationDescription,),
        attributes,
    )
    return description_class


# -- Classes ------------------------------------------------------------------


# pylint: disable=too-few-public-methods


class AccelerationDescription(IsDescription):
    """Description of HDF acceleration table"""

    counter = UInt8Col()
    """Message counter"""

    timestamp = UInt64Col()
    """Microseconds since measurement start"""


# pylint: enable=too-few-public-methods


class StorageException(Exception):
    """Exception for HDF storage errors"""


class Storage:
    """Context manager class for storing measurement data in HDF5 format

    Args:

        filepath:
            The filepath of the HDF5 file in which this object should store
            measurement data

        channels:
            All channels for which data should be collected or ``None``, if the
            axes data should be taken from an existing valid file at
            ``filepath``.

    Examples:

        Create new file

        >>> filepath = Path("test.hdf5")
        >>> with Storage(filepath,
        ...              channels=StreamingConfiguration(first=True)
        ... ) as storage:
        ...     pass

        Opening an non empty file but still providing channel info should fail

        >>> with Storage(filepath,
        ...             channels=StreamingConfiguration(first=True)
        ... ) as storage:
        ...     pass # doctest:+ELLIPSIS
        Traceback (most recent call last):
            ...
        ValueError: File “...” exist but channels parameter is not None
        >>> filepath.unlink()

    """

    def __init__(
        self,
        filepath: Path | str,
        channels: StreamingConfiguration | None = None,
    ) -> None:

        self.filepath = Path(filepath).expanduser().resolve()

        if (
            channels
            and self.filepath.exists()
            and self.filepath.stat().st_size != 0
        ):
            raise ValueError(
                f"File “{self.filepath}” exist but channels parameter "
                "is not None"
            )

        self.hdf: File | None = None
        self.channels = channels

    def __enter__(self) -> StorageData:
        """Open the HDF file for writing"""

        return self.open()

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Clean up the resources used by the storage class

        Args:

            exception_type:
                The type of the exception in case of an exception

            exception_value:
                The value of the exception in case of an exception

            traceback:
                The traceback in case of an exception

        """

        self.close()

    def open(self) -> StorageData:
        """Open and initialize the HDF file for writing"""

        try:
            self.hdf = open_file(
                self.filepath,
                mode="a",
                filters=Filters(4, "zlib"),
                title="STH Measurement Data",
            )
        except (HDF5ExtError, OSError) as error:
            raise StorageException(
                f"Unable to open file “{self.filepath}”: {error}"
            ) from error

        return StorageData(self.hdf, self.channels)

    def close(self) -> None:
        """Close the HDF file"""

        if isinstance(self.hdf, File) and self.hdf.isopen:
            self.hdf.close()


class StorageData:
    """Store HDF acceleration data

    Args:

        file_handle:
            The HDF file that should store the data

        channels:
            All channels for which data should be collected or ``None``, if the
            axes data should be taken from an existing valid file at
            ``filepath``.

    Examples:

        Create new data

        >>> filepath = Path("test.hdf5")
        >>> streaming_data = StreamingData(values=[1, 2, 3], counter=1,
        ...                                timestamp=4306978.449)
        >>> with Storage(filepath, StreamingConfiguration(first=True)) as data:
        ...     data.add_streaming_data(streaming_data)

        Read from existing file

        >>> with Storage(filepath) as data:
        ...     print(data.dataloss_stats())
        (1, 0)

        >>> filepath.unlink()

    """

    def __init__(
        self,
        file_handle: File,
        channels: StreamingConfiguration | None = None,
    ) -> None:

        self.hdf = file_handle
        self.start_time: float | None = None

        name = "acceleration"
        if channels:
            self.streaming_configuration = channels
            self.axes = channels.axes()
            self.acceleration = self.hdf.create_table(
                self.hdf.root,
                name=name,
                description=create_acceleration_description(
                    attributes={axis: Float32Col() for axis in self.axes}
                ),
                title="STH Acceleration Data",
            )
        else:
            try:
                self.acceleration = self.hdf.get_node(f"/{name}")
                streaming_config = {
                    "first": False,
                    "second": False,
                    "third": False,
                }
                for axis, channel in zip("xyz", streaming_config.keys()):
                    try:
                        getattr(self.acceleration.description, axis)
                        streaming_config[channel] = True
                    except AttributeError:
                        pass

                self.streaming_configuration = StreamingConfiguration(
                    **streaming_config
                )
                self.axes = self.streaming_configuration.axes()
                self.start_time = self.acceleration[-1][1] / 1000

            except NoSuchNodeError as error:
                raise StorageException(
                    f"Unable to open file “{self.hdf.filename}” due to "
                    f"incorrect format: {error}"
                ) from error

    def __getitem__(self, name: str) -> str:
        """Return acceleration metadata with the specified name

        Args:

            name:
                The name of the metadata this method should return

        Returns:

            The metadata with the specified name

        Examples:

            Import required library code

            >>> from pathlib import Path

            Write and read some metadata

            >>> filepath = Path("test.hdf5")
            >>> config = StreamingConfiguration(first=True)
            >>> with Storage(filepath, config) as storage:
            ...     storage.write_sensor_range(200)
            ...     print(storage["Sensor_Range"])
            ± 100 g₀
            >>> filepath.unlink()

        """

        return self.acceleration.attrs.__getitem__(name)

    def __setitem__(self, name: str, value: str) -> None:
        """Set acceleration metadata to a specific value

        Args:

            name:
                The name of the meta attribute

            value:
                The value of the meta attribute

        Examples:

            Store some example acceleration data

            >>> filepath = Path("test.hdf5")
            >>> with Storage(filepath,
            ...              StreamingConfiguration(third=True)) as storage:
            ...     storage["something"] =  "some value"
            ...     print(storage["something"])
            some value
            >>> filepath.unlink()

        """

        self.acceleration.attrs.__setitem__(name, value)

    def add_streaming_data(
        self,
        streaming_data: StreamingData,
    ) -> None:
        """Add streaming data to the storage object

        Args:

            streaming_data:
                The streaming data that should be added to the storage

        Examples:

            Import required library code

            >>> from icotronic.can.streaming import StreamingConfigBits

            Store streaming data for single channel

            >>> channel3 = StreamingConfiguration(first=False, second=False,
            ...                                   third=True)
            >>> data1 = StreamingData(values=[1, 2, 3], counter=21,
            ...                       timestamp=1)
            >>> data2 = StreamingData(values=[4, 5, 6], counter=22,
            ...                       timestamp=2)
            >>> filepath = Path("test.hdf5")
            >>> with Storage(filepath, channel3) as storage:
            ...     storage.add_streaming_data(data1)
            ...     storage.add_streaming_data(data2)
            ...     # Normally the class takes care about when to store back
            ...     # data to the disk itself. We do a manual flush here to
            ...     # check the number of stored items.
            ...     storage.acceleration.flush()
            ...     print(storage.acceleration.nrows)
            6
            >>> filepath.unlink()

            Store streaming data for three channels

            >>> all = StreamingConfiguration(first=True, second=True,
            ...                              third=True)
            >>> data1 = StreamingData(values=[1, 2, 3], counter=21,
            ...                       timestamp=1)
            >>> data2 = StreamingData(values=[4, 5, 6], counter=22,
            ...                       timestamp=2)
            >>> with Storage(filepath, all) as storage:
            ...     storage.add_streaming_data(data1)
            ...     storage.add_streaming_data(data2)
            ...     storage.acceleration.flush()
            ...     print(storage.acceleration.nrows)
            2
            >>> filepath.unlink()

        """

        values = streaming_data.values
        timestamp = streaming_data.timestamp
        counter = streaming_data.counter

        if self.start_time is None:
            self.start_time = timestamp
            self.acceleration.attrs["Start_Time"] = datetime.now().isoformat()

        assert isinstance(self.start_time, (int, float))

        row = self.acceleration.row
        timestamp = (timestamp - self.start_time) * 1_000_000

        if len(self.axes) == 1:
            axis = self.axes[0]
            for value in values:
                row["timestamp"] = timestamp
                row["counter"] = counter
                row[axis] = value
                row.append()
        else:
            row["timestamp"] = timestamp
            row["counter"] = counter
            for accelertation_type, value in zip(self.axes, values):
                row[accelertation_type] = value
            row.append()

    def write_sensor_range(self, sensor_range_in_g: float) -> None:
        """Add metadata about sensor range

        This method assumes that sensor have a symmetric measurement range
        (e.g. a sensor with a range of 200 g measures from - 100 g up to
        + 100 g).

        Args:

            sensor_range_in_g:
                The measurement range of the sensor in multiples of g

        Examples:

            Add sensor range metadata to example file

            >>> filepath = Path("test.hdf5")
            >>> with Storage(filepath,
            ...              StreamingConfiguration(third=True)) as storage:
            ...     storage.write_sensor_range(200)
            ...     print(storage.acceleration.attrs["Sensor_Range"])
            ± 100 g₀
            >>> filepath.unlink()

        """

        sensor_range_positive = round(sensor_range_in_g / 2)

        self["Sensor_Range"] = f"± {sensor_range_positive} g₀"

    def write_sample_rate(self, adc_configuration: ADCConfiguration) -> None:
        """Store the sample rate of the ADC

        Args:

            adc_configuration:
                The current ADC configuration of the sensor node

        Examples:

            Write and read sample rate metadata in example HDF file

            >>> filepath = Path("test.hdf5")
            >>> adc_configuration = ADCConfiguration(
            ...     set=True,
            ...     prescaler=2,
            ...     acquisition_time=16,
            ...     oversampling_rate=256)
            >>> with Storage(filepath,
            ...              StreamingConfiguration(first=True)) as storage:
            ...     storage.write_sample_rate(adc_configuration)
            ...     sample_rate = storage.acceleration.attrs["Sample_Rate"]
            ...     print(sample_rate) # doctest:+NORMALIZE_WHITESPACE
            1724.14 Hz (Prescaler: 2, Acquisition Time: 16,
            Oversampling Rate: 256)
            >>> filepath.unlink()

        """

        sample_rate = adc_configuration.sample_rate()

        adc_config_text = ", ".join([
            f"Prescaler: {adc_configuration.prescaler}",
            f"Acquisition Time: {adc_configuration.acquisition_time}",
            f"Oversampling Rate: {adc_configuration.oversampling_rate}",
        ])

        self["Sample_Rate"] = f"{sample_rate:.2f} Hz ({adc_config_text})"

    def dataloss_stats(self) -> tuple[int, int]:
        """Determine number of lost and received messages

        Returns:

            Tuple containing the number of received and the number of lost
            messages

        Examples:

            Get data loss statistics for an example file

            >>> def calculate_dataloss_stats():
            ...     filepath = Path("test.hdf5")
            ...     with Storage(filepath,StreamingConfiguration(
            ...                  first=True)) as storage:
            ...         for counter in range(256):
            ...             storage.add_streaming_data(
            ...                 StreamingData(values=[1, 2, 3],
            ...                               counter=counter,
            ...                               timestamp=counter/10))
            ...         for counter in range(128, 256):
            ...             storage.add_streaming_data(
            ...                 StreamingData(values=[4, 5, 6],
            ...                               counter=counter,
            ...                               timestamp=(255 + counter)/10))
            ...
            ...         stats = storage.dataloss_stats()
            ...     filepath.unlink()
            ...     return stats
            >>> retrieved, lost = calculate_dataloss_stats()
            >>> retrieved
            384
            >>> lost
            128

        """

        # Write back acceleration data so we can iterate over it
        self.acceleration.flush()

        stats = calculate_dataloss_stats(
            (int(record[0]) for record in self.acceleration)
        )

        return (stats.retrieved, stats.lost)

    def dataloss(self) -> float:
        """Determine (minimum) data loss

        Returns:

            Amount of lost messages divided by all messages (lost and
            retrieved)

        Examples:

            Import required library code

            >>> from math import isclose

            Calculate data loss for an example storage file

            >>> def calculate_dataloss():
            ...     filepath = Path("test.hdf5")
            ...     with Storage(filepath, StreamingConfiguration(
            ...                  first=True)) as storage:
            ...         for counter in range(256):
            ...             storage.add_streaming_data(
            ...                 StreamingData(values=[1, 2, 3],
            ...                               counter=counter,
            ...                               timestamp=counter/10))
            ...         for counter in range(128, 256):
            ...             storage.add_streaming_data(
            ...                 StreamingData(values=[4, 5, 6],
            ...                               counter=counter,
            ...                               timestamp=(255 + counter)/10))
            ...
            ...         dataloss = storage.dataloss()
            ...     filepath.unlink()
            ...     return dataloss
            >>> isclose(0.25, calculate_dataloss(), rel_tol=0.005)
            True

        """

        retrieved_messages, lost_messages = self.dataloss_stats()

        return MessageStats(
            retrieved=retrieved_messages, lost=lost_messages
        ).dataloss()

    def sampling_frequency(self) -> float:
        """Calculate sampling frequency of measurement data

        Returns:

            Sampling frequency (of a single data channel) in Hz

        Examples:

            Import required library code

            >>> from math import isclose

            Calculate sampling frequency for an example file

            >>> def calculate_sampling_frequency():
            ...     filepath = Path("test.hdf5")
            ...     with Storage(filepath, StreamingConfiguration(
            ...             first=True, second=True, third=True)) as storage:
            ...         storage.add_streaming_data(
            ...             StreamingData(values=[1, 2, 3],
            ...                           counter=1,
            ...                           timestamp=0))
            ...         storage.add_streaming_data(
            ...             StreamingData(values=[1, 2, 3],
            ...                           counter=2,
            ...                           timestamp=1))
            ...
            ...         sampling_frequency = storage.sampling_frequency()
            ...     filepath.unlink()
            ...     return sampling_frequency
            >>> calculate_sampling_frequency()
            2.0

        """

        retrieved_messages, lost_messages = self.dataloss_stats()
        messages = retrieved_messages + lost_messages
        rows_per_message = 3 if len(self.axes) == 1 else 1
        if len(self.acceleration) > 1:
            measurement_time_in_us = int(self.acceleration[-1]["timestamp"])
            return rows_per_message * messages * 10**6 / measurement_time_in_us

        return 0

    def measurement_time(self) -> int:
        """Get the measurement time

        Note:

            This method returns the value of the last timestamp. If there was
            dataloss at the end of the measurement, then the real measurement
            time might have been longer.

        Returns:

            The measurement time in microseconds

        """

        # Write back acceleration data so we can read last timestamp
        self.acceleration.flush()

        return (
            int(self.acceleration[-1]["timestamp"])
            if len(self.acceleration) > 1
            else 0
        )


# -- Main ---------------------------------------------------------------------

if __name__ == "__main__":
    from doctest import testmod

    testmod()
