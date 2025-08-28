"""Read and store some acceleration data of STH with node name Test-STH"""

# -- Imports ------------------------------------------------------------------

from asyncio import run
from pathlib import Path
from time import monotonic

from netaddr import EUI

from icotronic.can import Connection, StreamingConfiguration, STH
from icotronic.measurement import Storage

# -- Functions ----------------------------------------------------------------


async def store_streaming_data(identifier: EUI | str | int) -> None:
    """Store streaming data in HDF5 file

    Args:

        identifier:

            Identifier of STH node

    """

    async with Connection() as stu:
        async with stu.connect_sensor_node(identifier, STH) as sth:

            assert isinstance(sth, STH)  # Make type checker happy

            conversion_to_g = await sth.get_acceleration_conversion_function()

            filepath = Path("test.hdf5")
            stream_first = StreamingConfiguration(first=True)

            with Storage(filepath, channels=stream_first) as storage:
                # Store acceleration range as metadata
                storage.write_sensor_range(
                    await sth.get_acceleration_sensor_range_in_g()
                )
                # Store sampling rate (and ADC configuration as metadata)
                storage.write_sample_rate(await sth.get_adc_configuration())
                async with sth.open_data_stream(stream_first) as stream:
                    # Read data for about five seconds
                    end = monotonic() + 5
                    async for data, _ in stream:
                        # Convert from ADC bit value into multiples of g
                        storage.add_streaming_data(data.apply(conversion_to_g))
                        if monotonic() > end:
                            break


# -- Main ---------------------------------------------------------------------

if __name__ == "__main__":
    run(store_streaming_data(identifier="Test-STH"))
