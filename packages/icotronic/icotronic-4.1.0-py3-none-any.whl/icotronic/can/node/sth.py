"""Support for acceleration based sensor nodes (SHA and STH)"""

# -- Imports ------------------------------------------------------------------

from functools import partial
from collections.abc import Callable

from icotronic.can.calibration import CalibrationMeasurementFormat
from icotronic.can.node.eeprom.sth import STHEEPROM
from icotronic.can.protocol.message import Message
from icotronic.can.node.sensor import SensorNode
from icotronic.can.node.spu import SPU
from icotronic.measurement.acceleration import convert_raw_to_g
from icotronic.measurement.constants import ADC_MAX_VALUE

# -- Classes ------------------------------------------------------------------


class STH(SensorNode):
    """Communicate and control a connected SHA or STH

    Args:

        spu:
            The SPU object used to communicate with the node

    """

    def __init__(self, spu: SPU) -> None:

        super().__init__(spu, STHEEPROM)

    # ---------------------------
    # - Calibration Measurement -
    # ---------------------------

    async def _acceleration_self_test(
        self, activate: bool = True, dimension: str = "x"
    ) -> None:
        """Activate/Deactivate the accelerometer self test

        Args:

            activate:
                Either ``True`` to activate the self test or ``False`` to
                deactivate the self test

            dimension:
                The dimension (x=1, y=2, z=3) for which the self test should be
                activated/deactivated.

        """

        node = self.id
        method = "Activate" if activate else "Deactivate"

        try:
            dimension_number = "xyz".index(dimension) + 1
        except ValueError as error:
            raise ValueError(
                f"Invalid dimension value: “{dimension}”"
            ) from error

        message = Message(
            block="Configuration",
            block_command="Calibration Measurement",
            sender=self.spu.id,
            receiver=node,
            request=True,
            data=CalibrationMeasurementFormat(
                set=True,
                element="Data",
                method=method,
                dimension=dimension_number,
            ).data,
        )

        await self.spu.request(
            message,
            description=(
                f"{method.lower()} self test of {dimension}-axis of “{node}”"
            ),
        )

    async def activate_acceleration_self_test(
        self, dimension: str = "x"
    ) -> None:
        """Activate self test of STH accelerometer

        Args:

            dimension:
                The dimension (``x``, ``y`` or ``z``) for which the self test
                should be activated.

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Activate and deactivate acceleration self-test

            >>> async def test_self_test():
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is
            ...         # available
            ...         async with stu.connect_sensor_node(0, STH) as sth:
            ...             await sth.activate_acceleration_self_test()
            ...             await sth.deactivate_acceleration_self_test()
            >>> run(test_self_test())

        """

        await self._acceleration_self_test(activate=True, dimension=dimension)

    async def deactivate_acceleration_self_test(
        self, dimension: str = "x"
    ) -> None:
        """Deactivate self test of STH accelerometer

        Args:

            dimension:
                The dimension (``x``, ``y`` or ``z``) for which the self test
                should be deactivated.

        """

        await self._acceleration_self_test(activate=False, dimension=dimension)

    async def get_acceleration_voltage(
        self, dimension: str = "x", reference_voltage: float = 3.3
    ) -> float:
        """Retrieve the current acceleration voltage in Volt

        Args:

            dimension:
                The dimension (x=1, y=2, z=3) for which the acceleration
                voltage should be measured

            reference_voltage:
                The reference voltage for the ADC in Volt

        Returns:

            The voltage of the acceleration sensor in Volt

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the acceleration voltage of STH 1

            >>> async def read_acceleration_voltage():
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0, STH) as sth:
            ...             before = await sth.get_acceleration_voltage()
            ...             await sth.activate_acceleration_self_test()
            ...             between = await sth.get_acceleration_voltage()
            ...             await sth.deactivate_acceleration_self_test()
            ...             after = await sth.get_acceleration_voltage()
            ...         return (before, between, after)
            >>> before, between, after = run(read_acceleration_voltage())
            >>> before < between and after < between
            True

        """

        try:
            dimension_number = "xyz".index(dimension) + 1
        except ValueError as error:
            raise ValueError(
                f"Invalid dimension value: “{dimension}”"
            ) from error

        node = self.id
        message = Message(
            block="Configuration",
            block_command="Calibration Measurement",
            sender=self.spu.id,
            receiver=node,
            request=True,
            data=CalibrationMeasurementFormat(
                set=True,
                element="Data",
                method="Measure",
                reference_voltage=reference_voltage,
                dimension=dimension_number,
            ).data,
        )

        response = await self.spu.request(
            message, description=f"retrieve acceleration voltage of “{node}”"
        )

        adc_value = int.from_bytes(response.data[4:], "little")
        return adc_value / ADC_MAX_VALUE * reference_voltage

    async def get_acceleration_sensor_range_in_g(self) -> int:
        """Retrieve the maximum acceleration sensor range in multiples of g₀

        - For a ±100 g₀ sensor this method returns 200 (100 + abs(-100)).
        - For a ±50 g₀ sensor this method returns 100 (50 + abs(-50)).

        For this to work correctly the EEPROM value of the x-axis acceleration
        offset in the EEPROM has to be set.

        Returns:

            Range of current acceleration sensor in multiples of earth’s
            gravitation

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection
            >>> from icotronic.can.node.sth import STH

            Write and read the acceleration offset of STH 1

            >>> async def read_sensor_range():
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0, STH) as sth:
            ...             return (await
            ...                     sth.get_acceleration_sensor_range_in_g())
            >>> sensor_range = run(read_sensor_range())
            >>> 0 < sensor_range <= 200
            True

        """

        assert isinstance(self.eeprom, STHEEPROM)
        return round(
            abs(await self.eeprom.read_x_axis_acceleration_offset()) * 2
        )

    async def get_acceleration_conversion_function(
        self,
    ) -> Callable[[float], float]:
        """Retrieve function to convert raw sensor data into g

        Returns:

            A function that converts 16 bit raw values from the STH into
            multiples of earth’s gravitation (g)

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection
            >>> from icotronic.can.node.sth import STH

            Convert a raw ADC value into multiples of g

            >>> async def read_sensor_values():
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0, STH) as sth:
            ...             convert_to_g = (await
            ...                 sth.get_acceleration_conversion_function())
            ...             data = await sth.get_streaming_data_single()
            ...             before = list(data.values)
            ...             data.apply(convert_to_g)
            ...             return before, data.values
            >>> before, after = run(read_sensor_values())
            >>> all([0 <= value <= 2**16 for value in before])
            True
            >>> all([-100 <= value <= 100 for value in after])
            True

        """

        sensor_range = await self.get_acceleration_sensor_range_in_g()
        return partial(convert_raw_to_g, max_value=sensor_range)


# -- Main ---------------------------------------------------------------------

if __name__ == "__main__":
    from doctest import run_docstring_examples

    run_docstring_examples(
        STH.get_acceleration_conversion_function,
        globals(),
        verbose=True,
    )
