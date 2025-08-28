"""Read and write EEPROM data of ICOtronic sensor nodes"""

# -- Imports ------------------------------------------------------------------

from icotronic.can.constants import ADVERTISEMENT_TIME_EEPROM_TO_MS
from icotronic.can.node.eeprom.node import NodeEEPROM

# -- Sensor -------------------------------------------------------------------


class SensorNodeEEPROM(NodeEEPROM):
    """Read and write EEPROM data of sensor nodes"""

    # ========================
    # = System Configuration =
    # ========================

    async def read_sleep_time_1(self) -> int:
        """Retrieve sleep time 1 from the EEPROM

        Returns:

            The current value of sleep time 1 in milliseconds

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read sleep time 1 of the sensor node with node id 0

            >>> async def read_sleep_time_1():
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0) as sensor_node:
            ...             return await sensor_node.eeprom.read_sleep_time_1()
            >>> sleep_time = run(read_sleep_time_1())
            >>> isinstance(sleep_time, int)
            True

        """

        return await self.read_int(address=0, offset=9, length=4)

    async def write_sleep_time_1(self, milliseconds: int) -> None:
        """Write the value of sleep time 1 to the EEPROM

        Args:

            milliseconds:
                The value for sleep time 1 in milliseconds

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Write and read sleep time 1 of the sensor node with node id 0

            >>> async def write_read_sleep_time_1(milliseconds):
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0) as sensor_node:
            ...             await sensor_node.eeprom.write_sleep_time_1(
            ...                 milliseconds)
            ...             return await sensor_node.eeprom.read_sleep_time_1()
            >>> run(write_read_sleep_time_1(300_000))
            300000

        """

        await self.write_int(address=0, offset=9, value=milliseconds, length=4)

    async def read_advertisement_time_1(self) -> float:
        """Retrieve advertisement time 1 from the EEPROM

        Returns:

            The current value of advertisement time 1 in milliseconds

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read advertisement time 1 of of the sensor node with node id 0

            >>> async def read_advertisement_time_1():
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0) as sensor_node:
            ...             return await (
            ...                 sensor_node.eeprom.read_advertisement_time_1())
            >>> advertisement_time = run(read_advertisement_time_1())
            >>> isinstance(advertisement_time, float)
            True
            >>> advertisement_time > 0
            True

        """

        advertisement_time_eeprom = await self.read_int(
            address=0, offset=13, length=2
        )
        return advertisement_time_eeprom * ADVERTISEMENT_TIME_EEPROM_TO_MS

    async def write_advertisement_time_1(self, milliseconds: int):
        """Write the value of advertisement time 1 to the EEPROM

        Args:

            milliseconds:
                The value for advertisement time 1 in milliseconds

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Write and read advertisement time 1 of sensor node with node id 0

            >>> async def write_read_advertisement_time_1(milliseconds):
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0) as sensor_node:
            ...             await (
            ...                 sensor_node.eeprom.write_advertisement_time_1(
            ...                     milliseconds))
            ...             return await (
            ...                 sensor_node.eeprom.read_advertisement_time_1())
            >>> run(write_read_advertisement_time_1(1250))
            1250.0

        """

        advertisement_time_eeprom = round(
            milliseconds / ADVERTISEMENT_TIME_EEPROM_TO_MS
        )

        await self.write_int(
            address=0,
            offset=13,
            value=advertisement_time_eeprom,
            length=2,
        )

    async def read_sleep_time_2(self) -> int:
        """Retrieve sleep time 2 from the EEPROM

        Returns:

            The current value of sleep time 2 in milliseconds

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read sleep time 2 of sensor node with node id 0

            >>> async def read_sleep_time_2():
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0) as sensor_node:
            ...             return await sensor_node.eeprom.read_sleep_time_2()
            >>> sleep_time = run(read_sleep_time_2())
            >>> isinstance(sleep_time, int)
            True

        """

        return await self.read_int(address=0, offset=15, length=4)

    async def write_sleep_time_2(self, milliseconds: int) -> None:
        """Write the value of sleep time 2 to the EEPROM

        Args:

            milliseconds:
                The value for sleep time 2 in milliseconds

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Write and read sleep time 2 of sensor node with node id 0

            >>> async def write_read_sleep_time_2(milliseconds):
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0) as sensor_node:
            ...             await (sensor_node.eeprom.write_sleep_time_2(
            ...                    milliseconds))
            ...             return await sensor_node.eeprom.read_sleep_time_2()
            >>> run(write_read_sleep_time_2(259_200_000))
            259200000

        """

        await self.write_int(
            address=0, offset=15, value=milliseconds, length=4
        )

    async def read_advertisement_time_2(self) -> float:
        """Retrieve advertisement time 2 from the EEPROM

        Returns:

            The current value of advertisement time 2 in milliseconds

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read advertisement time 2 of sensor node with node id 0

            >>> async def read_advertisement_time_2():
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0) as sensor_node:
            ...             return await (
            ...                 sensor_node.eeprom.read_advertisement_time_2())
            >>> advertisement_time = run(read_advertisement_time_2())
            >>> isinstance(advertisement_time, float)
            True

        """

        advertisement_time_eeprom = await self.read_int(
            address=0, offset=19, length=2
        )

        return advertisement_time_eeprom * ADVERTISEMENT_TIME_EEPROM_TO_MS

    async def write_advertisement_time_2(self, milliseconds: int):
        """Write the value of advertisement time 2 to the EEPROM

        Args:

            milliseconds:
                The value for advertisement time 2 in milliseconds

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Write and read advertisement time 2 of sensor node with node id 0

            >>> async def write_read_advertisement_time_2(milliseconds):
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0) as sensor_node:
            ...             await (
            ...                 sensor_node.eeprom.write_advertisement_time_2(
            ...                 milliseconds))
            ...             return await (
            ...                 sensor_node.eeprom.read_advertisement_time_2())
            >>> run(write_read_advertisement_time_2(2500))
            2500.0

        """

        advertisement_time_eeprom = round(
            milliseconds / ADVERTISEMENT_TIME_EEPROM_TO_MS
        )

        await self.write_int(
            address=0, offset=19, value=advertisement_time_eeprom, length=2
        )


# -- Main ---------------------------------------------------------------------

if __name__ == "__main__":
    from doctest import run_docstring_examples

    run_docstring_examples(
        SensorNodeEEPROM.write_advertisement_time_2,
        globals(),
        verbose=True,
    )
