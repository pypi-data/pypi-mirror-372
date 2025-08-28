"""Read and write EEPROM data of ICOtronic sensory tool holders"""

# -- Imports ------------------------------------------------------------------

from icotronic.can.node.eeprom.sensor import SensorNodeEEPROM

# -- Sensor -------------------------------------------------------------------


class STHEEPROM(SensorNodeEEPROM):
    """Read and write EEPROM data of sensory tool holders"""

    # ===============
    # = Calibration =
    # ===============

    async def read_x_axis_acceleration_slope(self) -> float:
        """Retrieve the acceleration slope of the x-axis from the EEPROM

        Returns:

            The x-axis acceleration slope of the STH

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection
            >>> from icotronic.can.node.sth import STH

            Read x-axis acceleration slope of an STH with node number 0

            >>> async def read_x_axis_acceleration_slope():
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0, STH) as sth:
            ...             return ( await
            ...                 sth.eeprom.read_x_axis_acceleration_slope())
            >>> x_axis_acceleration_slope = run(
            ...     read_x_axis_acceleration_slope())
            >>> isinstance(x_axis_acceleration_slope, float)
            True

        """

        return await self.read_float(address=8, offset=0)

    async def write_x_axis_acceleration_slope(self, slope: float) -> None:
        """Write the acceleration slope of the x-axis to the EEPROM

        Args:

            slope:
                The addition to the acceleration value for one step of the ADC
                in multiples of g₀

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from math import isclose
            >>> from icotronic.can.connection import Connection
            >>> from icotronic.can.node.sth import STH

            Write and read the acceleration slope of an STH with node number 0

            >>> async def write_read_x_axis_acceleration_slope(slope):
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0, STH) as sth:
            ...             await (
            ...                 sth.eeprom.write_x_axis_acceleration_slope(
            ...                     slope))
            ...             return await (
            ...                 sth.eeprom.read_x_axis_acceleration_slope())
            >>> adc_max = 0xffff
            >>> acceleration_difference_max = 200
            >>> slope = acceleration_difference_max / adc_max
            >>> slope_read = run(write_read_x_axis_acceleration_slope(slope))
            >>> isclose(slope, slope_read)
            True

        """

        await self.write_float(address=8, offset=0, value=slope)

    async def read_x_axis_acceleration_offset(self) -> float:
        """Retrieve the acceleration offset of the x-axis from the EEPROM

        Returns:

            The acceleration offset of the x-axis of STH 1

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from platform import system
            >>> from icotronic.can.connection import Connection
            >>> from icotronic.can.node.sth import STH

            Read the acceleration offset of an STH with sensor node number 0

            >>> async def read_x_axis_acceleration_offset():
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0, STH) as sth:
            ...             return (await
            ...                 sth.eeprom.read_x_axis_acceleration_offset())
            >>> x_axis_acceleration_offset = run(
            ...     read_x_axis_acceleration_offset())
            >>> isinstance(x_axis_acceleration_offset, float)
            True

        """

        return await self.read_float(address=8, offset=4)

    async def write_x_axis_acceleration_offset(self, offset: int) -> None:
        """Write the acceleration offset of the x-axis to the EEPROM

        Args:

            offset:
                The (negative) offset of the acceleration value in multiples
                of g₀

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from math import isclose
            >>> from icotronic.can.connection import Connection
            >>> from icotronic.can.node.sth import STH

            Write and read the acceleration offset of an STH with number 0

            >>> async def write_read_x_axis_acceleration_offset(offset):
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0, STH) as sth:
            ...             await sth.eeprom.write_x_axis_acceleration_offset(
            ...                 offset)
            ...             return (await
            ...                 sth.eeprom.read_x_axis_acceleration_offset())
            >>> acceleration_difference_max = 200
            >>> offset = -(acceleration_difference_max/2)
            >>> offset_read = run(
            ...     write_read_x_axis_acceleration_offset(offset))
            >>> isclose(offset, offset_read)
            True

        """

        await self.write_float(address=8, offset=4, value=offset)

    async def read_y_axis_acceleration_slope(self) -> float:
        """Retrieve the acceleration slope of the y-axis from the EEPROM

        Returns:

            The y-axis acceleration slope of STH 1

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection
            >>> from icotronic.can.node.sth import STH

            Read the acceleration slope in the y direction of an STH

            >>> async def read_y_axis_acceleration_slope():
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0, STH) as sth:
            ...             return (await
            ...                 sth.eeprom.read_y_axis_acceleration_slope())
            >>> y_axis_acceleration_slope = run(
            ...     read_y_axis_acceleration_slope())
            >>> isinstance(y_axis_acceleration_slope, float)
            True

        """

        return await self.read_float(address=8, offset=8)

    async def write_y_axis_acceleration_slope(self, slope: float) -> None:
        """Write the acceleration slope of the y-axis to the EEPROM

        Args:

            slope:
                The addition to the acceleration value for one step of the ADC
                in multiples of g₀

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from math import isclose
            >>> from icotronic.can.connection import Connection
            >>> from icotronic.can.node.sth import STH

            Write and read the acceleration slope of STH 1

            >>> async def write_read_y_axis_acceleration_slope(slope):
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0, STH) as sth:
            ...             await (
            ...                 sth.eeprom.write_y_axis_acceleration_slope(
            ...                     slope))
            ...             return (await
            ...                 sth.eeprom.read_y_axis_acceleration_slope())
            >>> adc_max = 0xffff
            >>> acceleration_difference_max = 200
            >>> slope = acceleration_difference_max / adc_max
            >>> slope_read = run(write_read_y_axis_acceleration_slope(slope))
            >>> isclose(slope, slope_read)
            True

        """

        await self.write_float(address=8, offset=8, value=slope)

    async def read_y_axis_acceleration_offset(self) -> float:
        """Retrieve the acceleration offset of the y-axis from the EEPROM

        Returns:

            The acceleration offset of the y-axis of STH 1

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection
            >>> from icotronic.can.node.sth import STH

            Read the acceleration offset of STH 1

            >>> async def read_y_axis_acceleration_offset():
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0, STH) as sth:
            ...             return (await
            ...                 sth.eeprom.read_y_axis_acceleration_offset())
            >>> y_axis_acceleration_offset = run(
            ...     read_y_axis_acceleration_offset())
            >>> isinstance(y_axis_acceleration_offset, float)
            True

        """

        return await self.read_float(address=8, offset=12)

    async def write_y_axis_acceleration_offset(self, offset: int) -> None:
        """Write the acceleration offset of the y-axis to the EEPROM

        Args:

            offset:
                The (negative) offset of the acceleration value in multiples
                of g₀

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from math import isclose
            >>> from icotronic.can.connection import Connection
            >>> from icotronic.can.node.sth import STH

            Write and read the acceleration offset of STH 1

            >>> async def write_read_y_axis_acceleration_offset(offset):
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0, STH) as sth:
            ...             await sth.eeprom.write_y_axis_acceleration_offset(
            ...                 offset)
            ...             return (await
            ...                   sth.eeprom.read_y_axis_acceleration_offset())
            >>> acceleration_difference_max = 200
            >>> offset = -(acceleration_difference_max/2)
            >>> offset_read = run(
            ...     write_read_y_axis_acceleration_offset(offset))
            >>> isclose(offset, offset_read)
            True

        """

        await self.write_float(address=8, offset=12, value=offset)

    async def read_z_axis_acceleration_slope(self) -> float:
        """Retrieve the acceleration slope of the z-axis from the EEPROM

        Returns:

            The z-axis acceleration slope of the STH

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection
            >>> from icotronic.can.node.sth import STH

            Read the acceleration slope in the z direction of STH 1

            >>> async def read_z_axis_acceleration_slope():
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0, STH) as sth:
            ...             return (await
            ...                    sth.eeprom.read_z_axis_acceleration_slope())
            >>> z_axis_acceleration_slope = run(
            ...     read_z_axis_acceleration_slope())
            >>> isinstance(z_axis_acceleration_slope, float)
            True

        """

        return await self.read_float(address=8, offset=16)

    async def write_z_axis_acceleration_slope(self, slope: float) -> None:
        """Write the acceleration slope of the z-axis to the EEPROM

        Args:

            slope:
                The addition to the acceleration value for one step of the ADC
                in multiples of g₀

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from math import isclose
            >>> from icotronic.can.connection import Connection
            >>> from icotronic.can.node.sth import STH

            Write and read the acceleration slope of STH 1

            >>> async def write_read_z_axis_acceleration_slope(slope):
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0, STH) as sth:
            ...             (await
            ...                 sth.eeprom.write_z_axis_acceleration_slope(
            ...                 slope))
            ...             return (await
            ...                 sth.eeprom.read_z_axis_acceleration_slope())
            >>> adc_max = 0xffff
            >>> acceleration_difference_max = 200
            >>> slope = acceleration_difference_max / adc_max
            >>> slope_read = run(write_read_z_axis_acceleration_slope(slope))
            >>> isclose(slope, slope_read)
            True

        """

        await self.write_float(address=8, offset=16, value=slope)

    async def read_z_axis_acceleration_offset(self) -> float:
        """Retrieve the acceleration offset of the z-axis from the EEPROM

        Returns:

            The acceleration offset of the z-axis of STH 1

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection
            >>> from icotronic.can.node.sth import STH

            Read the acceleration offset of an STH

            >>> async def read_z_axis_acceleration_offset():
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0, STH) as sth:
            ...             return (await
            ...                 sth.eeprom.read_z_axis_acceleration_offset())
            >>> z_axis_acceleration_offset = run(
            ...     read_z_axis_acceleration_offset())
            >>> isinstance(z_axis_acceleration_offset, float)
            True

        """

        return await self.read_float(address=8, offset=20)

    async def write_z_axis_acceleration_offset(self, offset: int) -> None:
        """Write the acceleration offset of the z-axis to the EEPROM

        Args:

            offset:
                The (negative) offset of the acceleration value in multiples
                of g₀

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from math import isclose
            >>> from icotronic.can.connection import Connection
            >>> from icotronic.can.node.sth import STH

            Write and read the acceleration offset of an STH

            >>> async def write_read_z_axis_acceleration_offset(offset):
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0, STH) as sth:
            ...             await sth.eeprom.write_z_axis_acceleration_offset(
            ...                 offset)
            ...             return (await
            ...                 sth.eeprom.read_z_axis_acceleration_offset())
            >>> acceleration_difference_max = 200
            >>> offset = -(acceleration_difference_max/2)
            >>> offset_read = run(
            ...     write_read_z_axis_acceleration_offset(offset))
            >>> isclose(offset, offset_read)
            True

        """

        await self.write_float(address=8, offset=20, value=offset)


# -- Main ---------------------------------------------------------------------

if __name__ == "__main__":
    from doctest import run_docstring_examples

    run_docstring_examples(
        STHEEPROM.write_z_axis_acceleration_offset,
        globals(),
        verbose=True,
    )
