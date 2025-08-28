"""Test code for sensory milling head (SMH)"""

# -- Imports ------------------------------------------------------------------

from unittest import main as unittest_main

from icotronic.can.streaming import StreamingConfiguration
from icotronic.cmdline.commander import Commander
from icotronic.config import settings
from icotronic.measurement.sensor import guess_sensor, SensorConfiguration
from icotronic.report.report import Report
from icotronic.test.unit import ExtendedTestRunner
from icotronic.test.production.node import BaseTestCases, TestAttribute

# -- Classes ------------------------------------------------------------------


class TestSMH(BaseTestCases.TestSensorNode):
    """This class contains tests for the milling head sensor (PCB)"""

    @classmethod
    def setUpClass(cls):
        """Set up data for whole test"""

        super().setUpClass()
        cls.report = Report(node="SMH")
        # Guessed sensor types
        for sensor in range(1, settings.smh.channels + 1):
            cls.attributes[f"Sensor {sensor}"] = TestAttribute(str, pdf=True)

    async def _connect(self):
        """Create a connection to the SMH"""

        await super()._connect_node(settings.smh.name)

    async def _disconnect(self):
        """Tear down connection to SMH"""

        await super()._disconnect_node()

    def test__firmware_flash_disconnected(self):
        """Upload bootloader and application into SMH

        Note:

            The additional underscore in the method name that makes sure this
            test case is executed before all other test cases.

        Note:

            The text ``disconnected`` in the method name makes sure that the
            test framework does not initialize a connection.

        """

        self._test_firmware_flash(
            flash_location=settings.smh.firmware.location.flash,
            programmmer_serial_number=(
                settings.smh.programming_board.serial_number
            ),
            chip="BGM121A256V2",
        )

    async def test_eeprom(self):
        """Test if reading and writing the EEPROM works"""

        cls = type(self)

        # ========
        # = Name =
        # ========

        cls.attributes["Name"].value = await self._test_name(settings.smh.name)

        # =========================
        # = Sleep & Advertisement =
        # =========================

        await self._test_eeprom_sleep_advertisement_times()

        # ================
        # = Product Data =
        # ================

        await self._test_eeprom_product_data(settings.smh)

        # ==============
        # = Statistics =
        # ==============

        await self._test_eeprom_statistics(
            settings.smh.production_date,
            settings.smh.batch_number,
        )

    async def test_sensors(self):
        """Test available sensor channels"""

        async def read_streaming_data_amount(length: int):
            async with self.node.open_data_stream(
                StreamingConfiguration(first=True, second=False, third=False)
            ) as stream:
                stream_data = []
                async for data, _ in stream:
                    stream_data.extend(data.values)
                    if len(stream_data) >= length:
                        break

            # Due to the chosen streaming format the code above might have
            # collected one or two additional values. We remove these values
            # here.
            assert len(stream_data) >= length
            additional_values = len(stream_data) - length
            return stream_data[:-additional_values]

        cls = type(self)
        sensors = []

        for test_channel in range(1, settings.smh.channels + 1):
            await self.node.set_sensor_configuration(
                SensorConfiguration(first=test_channel)
            )
            config = await self.node.get_sensor_configuration()
            self.assertEqual(
                config.first,
                test_channel,
                f"Read sensor channel number “{config.first}” does "
                f"not match expected channel number “{test_channel}”",
            )
            stream_data = await read_streaming_data_amount(1000)
            sensor = guess_sensor(stream_data)
            sensors.append(sensor)
            cls.attributes[f"Sensor {test_channel}"].value = str(sensor)

        non_working_sensors = [
            str(sensor_number)
            for sensor_number, sensor in enumerate(sensors, start=1)
            if not sensor.works()
        ]

        if len(non_working_sensors) >= 1:
            if len(non_working_sensors) == 1:
                error_text = f"channel {non_working_sensors.pop()} seems"
            elif len(non_working_sensors) >= 2:
                channels = (
                    ", ".join(non_working_sensors[:-1])
                    + f" & {non_working_sensors[-1]}"
                )
                error_text = f"channels {channels} seem"
            plural = "" if len(non_working_sensors) <= 1 else "s"
            self.assertFalse(
                non_working_sensors,
                f"The sensor{plural} on measurement {error_text} "
                "to not work correctly.",
            )

    def test_power_usage_disconnected(self) -> None:
        """Check power usage in disconnected state"""

        commander = Commander(
            serial_number=settings.smh.programming_board.serial_number,
            chip="BGM121A256V2",
        )

        commander.enable_debug_mode()
        power_usage_mw = commander.read_power_usage()

        expected_maxmimum_usage_mw = 10
        self.assertLess(
            power_usage_mw,
            expected_maxmimum_usage_mw,
            f"Measured power usage of {power_usage_mw} mW is "
            "higher than expected maximum value "
            f"{expected_maxmimum_usage_mw} mW",
        )


# -- Main ---------------------------------------------------------------------


def main():
    """Run production test for Sensory Milling Head (SMH)"""

    unittest_main(
        testRunner=ExtendedTestRunner, module="icotronic.test.production.smh"
    )


if __name__ == "__main__":
    main()
