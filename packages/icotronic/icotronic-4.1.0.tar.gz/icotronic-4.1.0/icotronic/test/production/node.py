"""Test code for a single node in the ICOtronic system

The code below contains shared code for:

- SHA/STH
- SMH
- STU
"""

# -- Imports ------------------------------------------------------------------

from asyncio import get_running_loop, sleep
from datetime import date, datetime
from pathlib import Path
from typing import Any
from unittest import IsolatedAsyncioTestCase

from dynaconf.utils.boxing import DynaBox
from netaddr import EUI
from semantic_version import Version

from icotronic.can.connection import Connection
from icotronic.can.node.sth import STH
from icotronic.can.status import State
from icotronic.cmdline.commander import Commander
from icotronic.config import settings
from icotronic.can.node.eeprom.status import EEPROMStatus
from icotronic.report.report import Report
from icotronic.test.unit.extended_test_result import ExtendedTestResult
from icotronic import __version__

# -- Classes ------------------------------------------------------------------


class TestAttribute:
    """Test attribute that should be set to a value that is not ``None`` once

    Args:

        value:
            The value of the test attribute

        required_type:
            Stores type information about value

        unit:
            Optional unit for test attribute value

        pdf:
            Stores if the test attribute should be added to the test report or
            not

    Examples:

        Create an “empty” test attribute with type int

        >>> attribute = TestAttribute(int)
        >>> print(attribute.value)
        None

        Set a test attribute value later using the correct type

        >>> attribute.value = 1
        >>> attribute.value = 2

        Using an incorrect type will fail

        >>> attribute.value = "Something" # doctest:+ELLIPSIS
        Traceback (most recent call last):
           ...
        ValueError: The value “Something” is not ... type “<class 'int'>”
        >>> attribute.value
        2

        Initialize a test attribute with a certain value

        >>> TestAttribute(int, 5)
        5

    """

    def __init__(
        self,
        required_type: Any,
        value: Any = None,
        unit: str = "",
        pdf: bool = True,
    ) -> None:

        self.required_type = required_type
        self.value = value
        self.unit = unit
        self.pdf = pdf

    def __repr__(self) -> str:
        """Get a textual representation of the test attribute

        Returns:

            The textual representation of the test attribute

        Examples:

            Get string representation of an attribute with unit

            >>> TestAttribute(float, 11.0, "%")
            11.0 %

        """

        return f"{self.value}" + (f" {self.unit}" if self.unit else "")

    @property
    def value(self) -> Any:
        """Return the current value of the test attribute"""

        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        """Set the value of the test attribute

        Args:

            value:
                The new value of the test attribute

        Raises:

            ValueError:
                If the value is not ``None`` or does not have the required type

        """
        if value is None:
            self._value = None
            return

        if not isinstance(value, self.required_type):
            raise ValueError(
                f"The value “{value}” is not an instance of the required type "
                f"“{self.required_type}”"
            )

        self._value = value


# Use inner test class so we do not execute test methods of base class in
# addition to the test method of the super class.
# Source: https://stackoverflow.com/questions/1323455


# pylint: disable=too-few-public-methods
class BaseTestCases:
    """Collection of base test classes"""

    class TestNode(IsolatedAsyncioTestCase):
        """This class contains shared test code for STH and STU

        You are not supposed to use this class directly. Instead use it as base
        class for your test class.

        Every subclass of this class must set the attribute ``node`` to an
        object of the correct class (of ``can.node``).

        Please note, that this class only connects to the STU. If you also want
        to connect to a sensor node, please overwrite the method ``_connect``.

        To add additional test attributes shown in the standard output and
        optionally the PDF, add them to the **class** variable ``attributes``
        of this class or a subclass.

        The various ``_test`` methods in this class can be used to run certain
        tests for a node as part of a test method (i.e. a method that starts
        with the string ``test``).

        """

        attributes = {
            "Status": TestAttribute(str),
            "Name": TestAttribute(str),
            "Serial Number": TestAttribute(str, pdf=False),
            "GTIN": TestAttribute(int, pdf=False),
            "Bluetooth Address": TestAttribute(EUI),
            "Production Date": TestAttribute(date, pdf=False),
            "Hardware Version": TestAttribute(Version),
            "Batch Number": TestAttribute(int, pdf=False),
            "Firmware Version": TestAttribute(Version),
            "Release Name": TestAttribute(str, pdf=False),
            "EEPROM Status": TestAttribute(EEPROMStatus, pdf=False),
            "OEM Data": TestAttribute(str, pdf=False),
            "Operating Time": TestAttribute(int, pdf=False, unit="s"),
            "Power Off Cycles": TestAttribute(int, pdf=False),
            "Power On Cycles": TestAttribute(int, pdf=False),
            "Product Name": TestAttribute(str, pdf=False),
            "Under Voltage Counter": TestAttribute(int, pdf=False),
            "Watchdog Reset Counter": TestAttribute(int, pdf=False),
        }

        @classmethod
        def setUpClass(cls):
            """Set up data for whole test"""

            # Add a basic PDF report
            # Subclasses should overwrite this attribute, if you want to change
            # the default arguments of the report class
            cls.report = Report()

            # We store attributes related to the connection, such as MAC
            # address only once. To do that we set `read_attributes` to true
            # after the test class gathered the relevant data.
            cls.read_attributes = False

        @classmethod
        def tearDownClass(cls):
            """Print attributes of tested STH after all test cases"""

            cls.__output_general_data()
            cls.__output_node_data()
            cls.report.build()

        @classmethod
        def __output_general_data(cls):
            """Print general information and add it to PDF report"""

            now = datetime.now()

            attributes = {
                "ICOtronic Version": TestAttribute(
                    str, str(__version__), pdf=True
                ),
                "Date": TestAttribute(str, now.strftime("%Y-%m-%d"), pdf=True),
                "Time": TestAttribute(str, now.strftime("%H:%M:%S"), pdf=True),
                "Operator": TestAttribute(
                    str, settings.operator.name, pdf=True
                ),
            }

            cls.__output_data(attributes, node_data=False)

        @classmethod
        def __output_node_data(cls):
            """Print node information and add it to PDF report"""

            attributes = {
                description: (
                    TestAttribute(
                        str,
                        str(attribute.value),
                        unit=attribute.unit,
                        pdf=attribute.pdf,
                    )
                    if isinstance(
                        attribute.value, (date, EEPROMStatus, EUI, Version)
                    )
                    else attribute
                )
                for description, attribute in cls.attributes.items()
                if attribute.value is not None
            }

            cls.__output_data(attributes)

        @classmethod
        def __output_data(
            cls, attributes: dict[str, TestAttribute], node_data=True
        ) -> None:
            """Output data to standard output and PDF report

            Args:

                attributes:
                    The test attributes that should be printed

                node_data:
                    Specifies if this method outputs node specific or general
                    data

            """

            # Only output something, if there is at least one attribute
            if not attributes:
                return

            max_length_description = max(
                (len(description) for description in attributes)
            )
            max_length_value = max((
                len(str(attribute.value)) for attribute in attributes.values()
            ))

            # Print attributes to standard output
            print("\n")
            header = "Attributes" if node_data else "General"
            print(header)
            print("—" * len(header))

            for description, attribute in attributes.items():
                print(
                    f"{description:{max_length_description}} "
                    + f"{attribute.value:>{max_length_value}}"
                )

            # Add attributes to PDF
            attributes_pdf = {
                description: attribute
                for description, attribute in attributes.items()
                if attribute.pdf
            }

            assert hasattr(cls, "report")
            for description, attribute in attributes_pdf.items():
                cls.report.add_attribute(
                    description, attribute.value, node_data
                )

        async def asyncSetUp(self):
            """Set up hardware before a single test case"""

            # Disable debug mode (set by IsolatedAsyncioTestCase) to improve
            # runtime of code: https://github.com/python/cpython/issues/82789
            get_running_loop().set_debug(False)

            # All tests methods that contain the text `disconnected` do not
            # initialize a connection
            if self._testMethodName.find("disconnected") >= 0:
                return

            await self._connect()

            cls = type(self)
            # Only read node specific data once, even if we run multiple tests
            if not cls.read_attributes:
                cls.attributes["Bluetooth Address"].value = (
                    await self.node.get_mac_address()
                )
                cls.attributes["Firmware Version"].value = (
                    await self.node.get_firmware_version()
                )
                cls.attributes["Release Name"].value = (
                    await self.node.get_firmware_release_name()
                )
                cls.read_attributes = True

        async def asyncTearDown(self):
            """Clean up after single test case"""

            # All tests methods that contain the text `disconnected` do not
            # initialize a Bluetooth connection
            if self._testMethodName.find("disconnected") >= 0:
                return

            await self._disconnect()

        def run(self, result=None):
            """Execute a single test

            We override this method to store data about the test outcome.

            Args:

                result:
                     The unit test result of the test

            """

            super().run(result)
            if (
                not result.last_test.status
                == ExtendedTestResult.TestInformation.Status.SKIPPED
            ):
                type(self).report.add_test_result(
                    self.shortDescription(), result
                )

        async def _connect(self):
            """Create a connection to the STU"""

            # pylint: disable=attribute-defined-outside-init
            self.connection = Connection()
            # pylint: disable=unnecessary-dunder-call
            self.node = await self.connection.__aenter__()
            # pylint: enable=unnecessary-dunder-call
            # pylint: enable=attribute-defined-outside-init
            await self.node.reset()
            # Wait for reset to take place
            await sleep(2)

        async def _disconnect(self):
            """Tear down connection to STU"""

            await self.connection.__aexit__(None, None, None)

        async def test_connection(self):
            """Check connection to node"""

            # The sensor nodes need a little more time to switch from the
            # “Startup” to the “Operating” state
            await sleep(1)

            # Just send a request for the state and check, if the result
            # matches our expectations.
            state = await self.node.get_state()

            expected_state = State(
                mode="Get", location="Application", state="Operating"
            )

            self.assertEqual(
                expected_state,
                state,
                f"Expected state “{expected_state}” does not match "
                f"received state “{state}”",
            )

        def _test_firmware_flash(
            self,
            flash_location: str | Path,
            programmmer_serial_number: int,
            chip: str,
        ):
            """Upload bootloader and application into node

            Args:

                flash_location:
                    The location of the flash image

                programmer_serial_number:
                    The serial number of the programming board

                chip:
                    The name of the chip that should be flashed

            """

            image_filepath = Path(flash_location).expanduser().resolve()
            self.assertTrue(
                image_filepath.is_file(),
                f"Firmware file {image_filepath} does not exist",
            )

            commander = Commander(
                serial_number=programmmer_serial_number, chip=chip
            )

            commander.upload_flash(image_filepath)

        async def _test_eeprom_product_data(self, config: DynaBox) -> None:
            """Test if reading and writing the product data EEPROM page works

            Args:

                config
                    A configuration object that stores the various product data
                    attributes

            """

            cls = type(self)

            node = self.node

            # ========
            # = GTIN =
            # ========

            gtin = config.gtin
            await node.eeprom.write_gtin(gtin)
            cls.attributes["GTIN"].value = await node.eeprom.read_gtin()
            self.assertEqual(
                gtin,
                cls.attributes["GTIN"].value,
                f"Written GTIN “{gtin}” does not match read GTIN"
                f" “{cls.attributes['GTIN'].value}”",
            )

            # ====================
            # = Hardware Version =
            # ====================

            hardware_version = config.hardware_version
            await node.eeprom.write_hardware_version(hardware_version)
            cls.attributes["Hardware Version"].value = (
                await node.eeprom.read_hardware_version()
            )
            self.assertEqual(
                hardware_version,
                f"{cls.attributes['Hardware Version'].value}",
                f"Written hardware version “{hardware_version}” does not "
                + "match read hardware version"
                f" “{cls.attributes['Hardware Version'].value}”",
            )

            # ====================
            # = Firmware Version =
            # ====================

            await node.eeprom.write_firmware_version(
                cls.attributes["Firmware Version"].value
            )
            firmware_version = await node.eeprom.read_firmware_version()
            self.assertEqual(
                f"{cls.attributes['Firmware Version'].value}",
                f"{firmware_version}",
                "Written firmware version"
                f" “{cls.attributes['Firmware Version'].value}” does not "
                + f"match read firmware version “{firmware_version}”",
            )

            # ================
            # = Release Name =
            # ================

            # Originally we assumed that this value would be set by the
            # firmware itself. However, according to tests with an empty EEPROM
            # this is not the case.
            release_name = config.firmware.release_name
            await node.eeprom.write_release_name(release_name)
            cls.attributes["Release Name"].value = (
                await node.eeprom.read_release_name()
            )
            self.assertEqual(
                release_name,
                cls.attributes["Release Name"].value,
                f"Written firmware release name “{release_name}” does not "
                + "match read firmware release name"
                f" “{cls.attributes['Release Name'].value}”",
            )

            # =================
            # = Serial Number =
            # =================

            serial_number = config.serial_number
            await node.eeprom.write_serial_number(serial_number)
            cls.attributes["Serial Number"].value = (
                await node.eeprom.read_serial_number()
            )
            self.assertEqual(
                serial_number,
                cls.attributes["Serial Number"].value,
                f"Written serial number “{serial_number}” does not "
                + "match read serial number"
                f" “{cls.attributes['Serial Number'].value}”",
            )

            # ================
            # = Product Name =
            # ================

            product_name = config.product_name
            await node.eeprom.write_product_name(product_name)
            cls.attributes["Product Name"].value = (
                await node.eeprom.read_product_name()
            )
            self.assertEqual(
                product_name,
                cls.attributes["Product Name"].value,
                f"Written product name “{product_name}” does not "
                + "match read product name"
                f" “{cls.attributes['Product Name'].value}”",
            )

            # ============
            # = OEM Data =
            # ============

            oem_data = config.oem_data
            await node.eeprom.write_oem_data(oem_data)
            oem_data_list = await node.eeprom.read_oem_data()
            self.assertListEqual(
                oem_data,
                oem_data_list,
                f"Written OEM data “{oem_data}” does not "
                + f"match read OEM data “{oem_data_list}”",
            )
            # We currently store the data in text format, to improve the
            # readability of null bytes in the shell. Please notice, that this
            # will not always work (depending on the binary data stored in
            # EEPROM region).
            cls.attributes["OEM Data"].value = "".join(
                map(chr, oem_data_list)
            ).replace("\x00", "")

        async def _test_eeprom_statistics(
            self, production_date: date, batch_number: int
        ) -> None:
            """Test if reading and writing the statistics EEPROM page works

            For this purpose this method writes (default) values into the
            EEPROM, reads them and then checks if the written and read values
            are equal.

            Args:

                production_date:
                    The production date of the node

                batch_number:
                    The batch number of the node

            """

            cls = type(self)
            node = self.node

            # =======================
            # = Power On/Off Cycles =
            # =======================

            power_on_cycles = 0
            await node.eeprom.write_power_on_cycles(power_on_cycles)
            cls.attributes["Power On Cycles"].value = (
                await node.eeprom.read_power_on_cycles()
            )
            self.assertEqual(
                power_on_cycles,
                cls.attributes["Power On Cycles"].value,
                f"Written power on cycle value “{power_on_cycles}” "
                + "does not match read power on cycle value "
                + f"“{cls.attributes['Power On Cycles'].value}”",
            )

            power_off_cycles = 0
            await node.eeprom.write_power_off_cycles(power_off_cycles)
            cls.attributes["Power Off Cycles"].value = (
                await node.eeprom.read_power_off_cycles()
            )
            self.assertEqual(
                power_off_cycles,
                cls.attributes["Power Off Cycles"].value,
                f"Written power off cycle value “{power_off_cycles}” "
                + "does not match read power off cycle value "
                + f"“{cls.attributes['Power Off Cycles'].value}”",
            )

            # ==================
            # = Operating Time =
            # ==================

            operating_time = 0
            await node.eeprom.write_operating_time(operating_time)
            cls.attributes["Operating Time"].value = (
                await node.eeprom.read_operating_time()
            )
            self.assertEqual(
                operating_time,
                cls.attributes["Operating Time"].value,
                f"Written operating time “{operating_time}” "
                + "does not match read operating time"
                " “{cls.attributes['Operating Time'].value}”",
            )

            # =========================
            # = Under Voltage Counter =
            # =========================

            under_voltage_counter = 0
            await node.eeprom.write_under_voltage_counter(
                under_voltage_counter
            )
            cls.attributes["Under Voltage Counter"].value = (
                await node.eeprom.read_under_voltage_counter()
            )
            self.assertEqual(
                under_voltage_counter,
                cls.attributes["Under Voltage Counter"].value,
                "Written under voltage counter value"
                f" “{under_voltage_counter}” "
                + "does not match read under voltage counter value "
                + f"“{cls.attributes['Under Voltage Counter'].value}”",
            )

            # ==========================
            # = Watchdog Reset Counter =
            # ==========================

            watchdog_reset_counter = 0
            await node.eeprom.write_watchdog_reset_counter(
                watchdog_reset_counter
            )
            cls.attributes["Watchdog Reset Counter"].value = (
                await node.eeprom.read_watchdog_reset_counter()
            )
            self.assertEqual(
                watchdog_reset_counter,
                cls.attributes["Watchdog Reset Counter"].value,
                "Written watchdog reset counter value"
                f" “{watchdog_reset_counter} does not match read watchdog"
                " reset counter value"
                f" “{cls.attributes['Watchdog Reset Counter'].value}”",
            )

            # ===================
            # = Production Date =
            # ===================

            await node.eeprom.write_production_date(production_date)
            cls.attributes["Production Date"].value = (
                await node.eeprom.read_production_date()
            )
            self.assertEqual(
                production_date,
                cls.attributes["Production Date"].value,
                f"Written production date “{production_date}” does not match "
                + "read production date"
                f" “{cls.attributes['Production Date'].value}”",
            )

            # ================
            # = Batch Number =
            # ================

            await node.eeprom.write_batch_number(batch_number)
            cls.attributes["Batch Number"].value = (
                await node.eeprom.read_batch_number()
            )
            self.assertEqual(
                batch_number,
                cls.attributes["Batch Number"].value,
                f"Written batch “{batch_number}” does not match "
                + "read batch number"
                f" “{cls.attributes['Batch Number'].value}”",
            )

        async def _test_eeprom_status(self) -> None:
            """Test if reading and writing the EEPROM status byte works"""

            cls = type(self)
            node = self.node

            # =================
            # = EEPROM Status =
            # =================

            await node.eeprom.write_status("Initialized")
            cls.attributes["EEPROM Status"].value = (
                await node.eeprom.read_status()
            )
            self.assertTrue(
                cls.attributes["EEPROM Status"].value.is_initialized(),
                "Setting EEPROM status to “Initialized” failed. "
                "EEPROM status byte currently stores the value "
                f"“{cls.attributes['EEPROM Status'].value}”",
            )

    class TestSensorNode(TestNode):
        """This class contains support code for sensor node (SMH & STH)

        You are not supposed to use this class directly, but instead use it as
        superclass for your test class. For more information, please take a
        look at the documentation of ``TestNode``.

        """

        @classmethod
        def setUpClass(cls):
            """Set up data for whole test"""

            super().setUpClass()

            cls.attributes["RSSI"] = TestAttribute(int, unit="dBm")

            cls.attributes["Serial Number"] = TestAttribute(str)

            cls.attributes["Ratio Noise Maximum"] = TestAttribute(
                float, unit="dB"
            )
            cls.attributes["Sleep Time 1"] = TestAttribute(
                int, unit="ms", pdf=False
            )
            cls.attributes["Advertisement Time 1"] = TestAttribute(
                int, unit="ms", pdf=False
            )
            cls.attributes["Sleep Time 2"] = TestAttribute(
                int, unit="ms", pdf=False
            )
            cls.attributes["Advertisement Time 2"] = TestAttribute(
                int, unit="ms", pdf=False
            )

        async def _connect_node(self, name: str) -> None:
            """Create a connection to the node with the specified name

            Args:

                name:
                    The (Bluetooth advertisement) name of the sensor node

            """

            await super()._connect()  # Connect to STU
            stu = self.node

            # pylint: disable=attribute-defined-outside-init
            self.sensor_node_connection = stu.connect_sensor_node(name, STH)
            # New node is sensor node
            # pylint: disable=unnecessary-dunder-call
            self.node = await self.sensor_node_connection.__aenter__()
            # pylint: enable=unnecessary-dunder-call
            self.stu = stu

            cls = type(self)
            cls.attributes["RSSI"].value = await self.node.get_rssi()

        async def _disconnect_node(self) -> None:
            """Disconnect from sensor node and STU"""

            await self.sensor_node_connection.__aexit__(None, None, None)
            await super()._disconnect()  # Disconnect from STU

        async def _test_name(self, name: str) -> str:
            """Check if writing and reading the name of a sensor node works

            Args:

                name:
                    The text that should be used as name for the sensor node

            Returns:

                Read back name

            """

            node = self.node
            await node.eeprom.write_name(name)
            read_name = await node.eeprom.read_name()

            self.assertEqual(
                name,
                read_name,
                f"Written name “{name}” does not match read name"
                f" “{read_name}”",
            )

            return read_name

        async def _test_eeprom_sleep_advertisement_times(self):
            """Test if reading and writing sleep/advertisement times works"""

            async def read_write_time(
                read_function,
                write_function,
                attribute,
                milliseconds,
            ):
                await write_function(milliseconds)
                milliseconds_read = round(await read_function())
                type(self).attributes[attribute].value = milliseconds_read
                self.assertEqual(
                    milliseconds_read,
                    milliseconds,
                    f"Value {milliseconds_read} ms of “{attribute}” does not "
                    f"match written value of {milliseconds} ms",
                )

            await read_write_time(
                read_function=self.node.eeprom.read_sleep_time_1,
                write_function=self.node.eeprom.write_sleep_time_1,
                attribute="Sleep Time 1",
                milliseconds=settings.sensor_node.bluetooth.sleep_time_1,
            )

            await read_write_time(
                read_function=self.node.eeprom.read_advertisement_time_1,
                write_function=self.node.eeprom.write_advertisement_time_1,
                attribute="Advertisement Time 1",
                milliseconds=(
                    settings.sensor_node.bluetooth.advertisement_time_1
                ),
            )

            await read_write_time(
                read_function=self.node.eeprom.read_sleep_time_2,
                write_function=self.node.eeprom.write_sleep_time_2,
                attribute="Sleep Time 2",
                milliseconds=settings.sensor_node.bluetooth.sleep_time_2,
            )

            await read_write_time(
                read_function=self.node.eeprom.read_advertisement_time_2,
                write_function=self.node.eeprom.write_advertisement_time_2,
                attribute="Advertisement Time 2",
                milliseconds=(
                    settings.sensor_node.bluetooth.advertisement_time_2
                ),
            )


# pylint: enable=too-few-public-methods

if __name__ == "__main__":
    from doctest import testmod

    testmod()
