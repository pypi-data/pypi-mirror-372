"""Node specific EEPROM support"""

# -- Imports ------------------------------------------------------------------

from datetime import date

from semantic_version import Version

from icotronic.can.node.eeprom.basic import EEPROM
from icotronic.can.node.eeprom.status import EEPROMStatus

# -- Classes ------------------------------------------------------------------

# pylint: disable=too-many-public-methods


class NodeEEPROM(EEPROM):
    """Read and write node specific EEPROM data (STU/sensor nodes)"""

    # ========================
    # = System Configuration =
    # ========================

    async def read_status(self) -> EEPROMStatus:
        """Retrieve EEPROM status byte

        Returns:

            An EEPROM status object for the current status byte value

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the status byte of STU 1

            >>> async def read_status_byte():
            ...     async with Connection() as stu:
            ...         return await stu.eeprom.read_status()
            >>> isinstance(run(read_status_byte()), EEPROMStatus)
            True

        """

        return EEPROMStatus(
            (await self.read(address=0, offset=0, length=1)).pop()
        )

    async def write_status(self, value: int | EEPROMStatus) -> None:
        """Change the value of the EEPROM status byte

        Args:

            value:
                The new value for the status byte


        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Write and read the status byte of STU 1

            >>> async def write_read_status_byte():
            ...     async with Connection() as stu:
            ...         await stu.eeprom.write_status(
            ...             EEPROMStatus('Initialized'))
            ...         return await stu.eeprom.read_status()
            >>> status = run(write_read_status_byte())
            >>> status.is_initialized()
            True

        """

        await self.write_int(
            address=0, offset=0, length=1, value=EEPROMStatus(value).value
        )

    async def read_name(self) -> str:
        """Retrieve the name of the node from the EEPROM

        Returns:

            The name of the node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the name of STU 1

            >>> async def read_name():
            ...     async with Connection() as stu:
            ...         return await stu.eeprom.read_name()
            >>> isinstance(run(read_name()), str)
            True

        """

        return await self.read_text(address=0, offset=1, length=8)

    async def write_name(self, name: str) -> None:
        """Write the name of the node into the EEPROM

        Args:

            name:
                The new (Bluetooth advertisement) name of the node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Write and read the name of STU 1

            >>> async def write_read_name(name):
            ...     async with Connection() as stu:
            ...         await stu.eeprom.write_name(name)
            ...         return await stu.eeprom.read_name()
            >>> run(write_read_name('Valerie'))
            'Valerie'

        """

        await self.write_text(address=0, offset=1, text=name, length=8)

    # ================
    # = Product Data =
    # ================

    async def read_gtin(self) -> int:
        """Read the global trade identifier number (GTIN) from the EEPROM

        Returns:

            The GTIN of the specified node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the GTIN of STU 1

            >>> async def read_gtin():
            ...     async with Connection() as stu:
            ...         return await stu.eeprom.read_gtin()
            >>> gtin = run(read_gtin())
            >>> isinstance(gtin, int)
            True

        """

        return await self.read_int(address=4, offset=0, length=8)

    async def write_gtin(self, gtin: int) -> None:
        """Write the global trade identifier number (GTIN) to the EEPROM

        Args:

            gtin:
                The new GTIN of the specified receiver

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Write and read the GTIN of STU 1

            >>> async def write_read_gtin(gtin):
            ...     async with Connection() as stu:
            ...         await stu.eeprom.write_gtin(gtin=gtin)
            ...         return await stu.eeprom.read_gtin()
            >>> run(write_read_gtin(0))
            0

        """

        await self.write_int(address=4, offset=0, length=8, value=gtin)

    async def read_hardware_version(self) -> Version:
        """Read the current hardware version from the EEPROM

        Returns:

            The hardware version of the node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the hardware version of STU 1

            >>> async def read_hardware_version():
            ...     async with Connection() as stu:
            ...         return (await stu.eeprom.read_hardware_version())
            >>> hardware_version = run(read_hardware_version())
            >>> hardware_version.major >= 1
            True

        """

        major, minor, patch = await self.read(address=4, offset=13, length=3)
        return Version(major=major, minor=minor, patch=patch)

    async def write_hardware_version(self, version: str | Version):
        """Write hardware version to the EEPROM

        Args:

            version:
                The new hardware version of the node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Write and read the hardware version of STU 1

            >>> async def write_read_hardware_version(version):
            ...     async with Connection() as stu:
            ...         await stu.eeprom.write_hardware_version(version)
            ...         return (await stu.eeprom.read_hardware_version())
            >>> hardware_version = run(write_read_hardware_version('1.3.2'))
            >>> hardware_version.patch == 2
            True

        """

        if isinstance(version, str):
            version = Version(version)

        await self.write(
            address=4,
            offset=13,
            length=3,
            data=[version.major, version.minor, version.patch],
        )

    async def read_firmware_version(self) -> Version:
        """Retrieve the current firmware version from the EEPROM

        Returns:

            The firmware version of the node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the firmware version of STU 1

            >>> async def read_firmware_version():
            ...     async with Connection() as stu:
            ...         return await stu.eeprom.read_firmware_version()
            >>> firmware_version = run(read_firmware_version())
            >>> firmware_version.major >= 2
            True

        """

        major, minor, patch = await self.read(address=4, offset=21, length=3)
        return Version(major=major, minor=minor, patch=patch)

    async def write_firmware_version(self, version: str | Version) -> None:
        """Write firmware version to the EEPROM

        Args:

            version:
                The new firmware version

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Write and read the firmware version of STU 1

            >>> async def write_read_firmware_version(version):
            ...     async with Connection() as stu:
            ...         await stu.eeprom.write_firmware_version(version)
            ...         return (await stu.eeprom.read_firmware_version())
            >>> version = '2.1.10'
            >>> firmware_version = run(write_read_firmware_version(version))
            >>> firmware_version == Version(version)
            True

        """

        if isinstance(version, str):
            version = Version(version)

        await self.write(
            address=4,
            offset=21,
            length=3,
            data=[version.major, version.minor, version.patch],
        )

    async def read_release_name(self) -> str:
        """Retrieve the current release name from the EEPROM

        Returns:

            The firmware release name of the specified node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the release name of STU 1

            >>> async def read_release_name():
            ...     async with Connection() as stu:
            ...         return await stu.eeprom.read_release_name()
            >>> run(read_release_name())
            'Valerie'

        """

        return await self.read_text(address=4, offset=24, length=8)

    async def write_release_name(self, name: str):
        """Write the release name to the EEPROM

        Args:

            name:
                The new name of the release

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Write and read the release name of STU 1

            >>> async def write_read_release_name(name):
            ...     async with Connection() as stu:
            ...         await stu.eeprom.write_release_name(name)
            ...         return await stu.eeprom.read_release_name()
            >>> run(write_read_release_name('Valerie'))
            'Valerie'

        """

        await self.write_text(address=4, offset=24, length=8, text=name)

    async def read_serial_number(self) -> str:
        """Retrieve the serial number from the EEPROM

        Returns:

            The serial number of the node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the serial number of STU 1

            >>> async def read_serial_number():
            ...     async with Connection() as stu:
            ...         return await stu.eeprom.read_serial_number()
            >>> serial_number = run(read_serial_number())
            >>> isinstance(serial_number, str)
            True

        """

        return await self.read_text(address=4, offset=32, length=32)

    async def write_serial_number(self, serial_number: str):
        """Write the serial number to the EEPROM

        Args:

            serial_number:
                The serial number of the specified receiver

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Write and read the serial number of STU 1

            >>> async def write_read_serial_number(serial):
            ...     async with Connection() as stu:
            ...         await stu.eeprom.write_serial_number(serial)
            ...         return await stu.eeprom.read_serial_number()
            >>> run(write_read_serial_number('0'))
            '0'

        """

        await self.write_text(
            address=4, offset=32, length=32, text=serial_number
        )

    async def read_product_name(self) -> str:
        """Retrieve the product name from the EEPROM

        Returns:

            The product name of the node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the product name of STU 1

            >>> async def read_product_name():
            ...     async with Connection() as stu:
            ...         return await stu.eeprom.read_product_name()
            >>> product_name = run(read_product_name())
            >>> isinstance(product_name, str)
            True

        """

        return await self.read_text(address=4, offset=64, length=128)

    async def write_product_name(self, name: str):
        """Write the product name to the EEPROM

        Args:

            name:
                The new product name of the specified receiver

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Write and read the product name of STU 1

            >>> async def write_read_product_name(name):
            ...     async with Connection() as stu:
            ...         await stu.eeprom.write_product_name(name)
            ...         return await stu.eeprom.read_product_name()
            >>> run(write_read_product_name('0'))
            '0'

        """

        await self.write_text(address=4, offset=64, length=128, text=name)

    async def read_oem_data(self) -> list[int]:
        """Retrieve the OEM data from the EEPROM

        Returns:

            The OEM data of the specified node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the OEM data of STU 1

            >>> async def read_oem_data():
            ...     async with Connection() as stu:
            ...         return await stu.eeprom.read_oem_data()
            >>> oem_data = run(read_oem_data())
            >>> len(oem_data) == 64
            True

        """

        return await self.read(address=4, offset=192, length=64)

    async def write_oem_data(self, data: list[int]):
        """Write OEM data to the EEPROM

        Args:

            data:
                The OEM data that should be stored in the EEPROM

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Write and read the OEM data of STU 1

            >>> async def write_read_oem_data(data):
            ...     async with Connection() as stu:
            ...         await stu.eeprom.write_oem_data(data)
            ...         return await stu.eeprom.read_oem_data()
            >>> data = [0] * 64
            >>> run(write_read_oem_data(data)) == data
            True

        """

        await self.write(address=4, offset=192, length=64, data=data)

    # ==============
    # = Statistics =
    # ==============

    async def read_power_on_cycles(self) -> int:
        """Retrieve the number of power on cycles from the EEPROM

        Returns:

            The number of power on cycles of the node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the number of power on cycles of STU 1

            >>> async def read_power_on_cycles():
            ...     async with Connection() as stu:
            ...         return await stu.eeprom.read_power_on_cycles()
            >>> power_on_cycles = run(read_power_on_cycles())
            >>> power_on_cycles >= 0
            True

        """

        return await self.read_int(address=5, offset=0, length=4)

    async def write_power_on_cycles(self, times: int):
        """Write the number of power on cycles to the EEPROM

        Args:

            times:
                The number of power on cycles that should be stored in the
                EEPROM

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Write and read the number of power on cycles of STU 1

            >>> async def write_read_power_on_cycles(times):
            ...     async with Connection() as stu:
            ...         await stu.eeprom.write_power_on_cycles(times)
            ...         return await stu.eeprom.read_power_on_cycles()
            >>> run(write_read_power_on_cycles(0))
            0

        """

        await self.write_int(address=5, offset=0, length=4, value=times)

    async def read_power_off_cycles(self) -> int:
        """Retrieve the number of power off cycles from the EEPROM

        Returns:

            The number of power off cycles of the node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the number of power off cycles of STU 1

            >>> async def read_power_off_cycles():
            ...     async with Connection() as stu:
            ...         return await stu.eeprom.read_power_off_cycles()
            >>> power_off_cycles = run(read_power_off_cycles())
            >>> power_off_cycles >= 0
            True

        """

        return await self.read_int(address=5, offset=4, length=4)

    async def write_power_off_cycles(self, times: int):
        """Write the number of power off cycles to the EEPROM

        Args:

            times:
                The number of power off cycles that should be stored in the
                EEPROM

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Write and read the number of power off cycles of STU 1

            >>> async def write_read_power_off_cycles(times):
            ...     async with Connection() as stu:
            ...         await stu.eeprom.write_power_off_cycles(times)
            ...         return await stu.eeprom.read_power_off_cycles()
            >>> run(write_read_power_off_cycles(0))
            0

        """

        await self.write_int(address=5, offset=4, length=4, value=times)

    async def read_operating_time(self) -> int:
        """Retrieve the operating time from the EEPROM

        Returns:

            The operating time of the node in seconds

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the operating time of STU 1

            >>> async def read_operating_time():
            ...     async with Connection() as stu:
            ...         return await stu.eeprom.read_operating_time()
            >>> operating_time = run(read_operating_time())
            >>> operating_time >= 0
            True

        """

        return await self.read_int(address=5, offset=8, length=4)

    async def write_operating_time(self, seconds: int):
        """Write operating time to the EEPROM

        Args:

            seconds:
                The operating time in seconds that should be stored in the
                EEPROM

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Write and read the operating time of STU 1

            >>> async def write_read_operating_time(seconds):
            ...     async with Connection() as stu:
            ...         await stu.eeprom.write_operating_time(seconds)
            ...         return await stu.eeprom.read_operating_time()
            >>> operating_time = run(write_read_operating_time(10))
            >>> 10 <= operating_time <= 11
            True

        """

        await self.write_int(address=5, offset=8, length=4, value=seconds)

    async def read_under_voltage_counter(self) -> int:
        """Retrieve the under voltage counter value from the EEPROM

        Returns:

            The number of times the voltage was too low for the node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the under voltage counter of STU 1

            >>> async def read_under_voltage_counter():
            ...     async with Connection() as stu:
            ...         return await stu.eeprom.read_under_voltage_counter()
            >>> under_voltage_counter = run(read_under_voltage_counter())
            >>> under_voltage_counter >= 0
            True

        """

        return await self.read_int(address=5, offset=12, length=4)

    async def write_under_voltage_counter(self, times: int):
        """Write the under voltage counter value to the EEPROM

        Args:

            times:
                The number of times the voltage was too low

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Write and read the under voltage counter of STU 1

            >>> async def write_read_under_voltage_counter(times):
            ...     async with Connection() as stu:
            ...         await stu.eeprom.write_under_voltage_counter(times)
            ...         return await stu.eeprom.read_under_voltage_counter()
            >>> run(write_read_under_voltage_counter(0))
            0

        """

        await self.write_int(address=5, offset=12, length=4, value=times)

    async def read_watchdog_reset_counter(self) -> int:
        """Retrieve the watchdog reset counter value from the EEPROM

        Returns:

            The watchdog reset counter value of the node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the watchdog reset counter of STU 1

            >>> async def read_watchdog_reset_counter():
            ...     async with Connection() as stu:
            ...         return await stu.eeprom.read_watchdog_reset_counter()
            >>> watchdog_reset_counter = run(read_watchdog_reset_counter())
            >>> watchdog_reset_counter >= 0
            True

        """

        return await self.read_int(address=5, offset=16, length=4)

    async def write_watchdog_reset_counter(self, times: int) -> None:
        """Write the watchdog reset counter value to the EEPROM

        Args:

            times:
                The value of the watchdog reset counter for the specified node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Write and read the watchdog reset counter of STU 1

            >>> async def write_read_watchdog_reset_counter(times):
            ...     async with Connection() as stu:
            ...         await stu.eeprom.write_watchdog_reset_counter(times)
            ...         return await stu.eeprom.read_watchdog_reset_counter()
            >>> run(write_read_watchdog_reset_counter(0))
            0

        """

        await self.write_int(address=5, offset=16, length=4, value=times)

    async def read_production_date(self) -> date:
        """Retrieve the production date from the EEPROM

        Returns:

            The production date of the specified node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the production date of STU 1

            >>> async def read_production_date():
            ...     async with Connection() as stu:
            ...         return await stu.eeprom.read_production_date()
            >>> production_date = run(read_production_date())
            >>> isinstance(production_date, date)
            True

        """

        date_values = await self.read_text(address=5, offset=20, length=8)
        return date(
            year=int(date_values[0:4]),
            month=int(date_values[4:6]),
            day=int(date_values[6:8]),
        )

    # pylint: disable=redefined-outer-name

    async def write_production_date(self, date: date | str) -> None:
        """Write the production date to the EEPROM

        Args:

            date:
                The production date of the specified node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Write and read the production date of STU 1

            >>> async def write_read_production_date(date):
            ...     async with Connection() as stu:
            ...         await stu.eeprom.write_production_date(date=date)
            ...         return await stu.eeprom.read_production_date()

            >>> production_date = date(year=2020, month=10, day=5)
            >>> str(run(write_read_production_date(production_date)))
            '2020-10-05'

            >>> production_date = '2000-01-05'
            >>> str(run(write_read_production_date(production_date)))
            '2000-01-05'

        """

        if isinstance(date, str):
            # The identifier `date` refers to the variable `date` in the
            # current scope
            import datetime  # pylint: disable=import-outside-toplevel

            try:
                date = datetime.date.fromisoformat(date)
            except ValueError as error:
                raise ValueError(
                    f"Invalid value for date argument: “{date}”"
                ) from error

        await self.write_text(
            address=5,
            offset=20,
            length=8,
            text=str(date).replace("-", ""),
        )

    # pylint: enable=redefined-outer-name

    async def read_batch_number(self) -> int:
        """Retrieve the batch number from the EEPROM

        Returns:

            The batch number of the node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the batch number of STU 1

            >>> async def read_batch_number():
            ...     async with Connection() as stu:
            ...         return await stu.eeprom.read_batch_number()
            >>> batch_number = run(read_batch_number())
            >>> isinstance(batch_number, int)
            True

        """

        return await self.read_int(address=5, offset=28, length=4)

    async def write_batch_number(self, number: int) -> None:
        """Write the batch number to the EEPROM

        Args:

            number:
                The batch number of the node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Write and read the batch number of STU 1

            >>> async def write_read_batch_number(number):
            ...     async with Connection() as stu:
            ...         await stu.eeprom.write_batch_number(number)
            ...         return await stu.eeprom.read_batch_number()
            >>> run(write_read_batch_number(1337))
            1337

        """

        await self.write_int(address=5, offset=28, length=4, value=number)


# pylint: enable=too-many-public-methods

# -- Main ---------------------------------------------------------------------

if __name__ == "__main__":
    from doctest import testmod

    testmod()
