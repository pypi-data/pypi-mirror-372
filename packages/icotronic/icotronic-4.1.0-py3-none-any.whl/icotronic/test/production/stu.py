"""Test code for stationary transceiver unit (STU)"""

# -- Imports ------------------------------------------------------------------

import sys
import threading

from asyncio import sleep
from os import devnull
from sys import stderr
from unittest import main as unittest_main

from icotronic.can.connection import Connection
from icotronic.config import settings
from icotronic.report.report import Report
from icotronic.test.unit import ExtendedTestRunner
from icotronic.can.error import CANInitError, NoResponseError
from icotronic.test.production.node import BaseTestCases

# -- Class --------------------------------------------------------------------


class TestSTU(BaseTestCases.TestNode):
    """This class contains tests for the Stationary Transceiver Unit (STU)"""

    @classmethod
    def setUpClass(cls):
        """Set up data for whole test"""

        super().setUpClass()
        cls.report = Report(node="STU")

    async def test__firmware_flash_disconnected(self):
        """Upload bootloader and application into STU

        Note:

            The additional underscore in the method name that makes sure this
            test case is executed before all other test cases.

        Note:

            The text ``disconnected`` in the method name makes sure that the
            test framework does not initialize a connection.

        """

        self._test_firmware_flash(
            flash_location=settings.stu.firmware.location.flash,
            programmmer_serial_number=(
                settings.stu.programming_board.serial_number
            ),
            chip="BGM111A256V2",
        )

        # Try to Fix CAN connection problems after firmware update

        # Ignore errors in notifier thread
        old_excepthook = threading.excepthook
        threading.excepthook = lambda *args, **kwargs: print("", end="")

        old_stderr = sys.stderr
        with open(devnull, "w", encoding="utf8") as stream_devnull:
            # Do not print error output
            sys.stderr = stream_devnull

            status_ok = False
            attempt = 1
            while not status_ok and attempt <= 10:
                print(
                    f"\nTrying to fix CAN connection (Attempt {attempt})",
                    end="",
                )
                try:
                    async with Connection() as stu:
                        await stu.reset()
                    status_ok = True

                except CANInitError:
                    # Init error only seems to happen on the **first
                    # attempt**, if the CAN adapter is not connected to the
                    # computer.
                    if attempt == 1:
                        print("\nCAN adapter is not connected → Exiting\n")
                        return

                    await sleep(1)
                except NoResponseError:
                    await sleep(1)

                attempt += 1
            print()

        # Reenable error output
        sys.stderr = old_stderr
        # Show errors in notifier threads again
        threading.excepthook = old_excepthook

        if not status_ok:
            print("Unable to fix CAN connection", file=stderr)

    async def test_eeprom(self):
        """Test if reading and writing the EEPROM works"""

        # ================
        # = Product Data =
        # ================

        await self._test_eeprom_product_data(settings.stu)

        # ==============
        # = Statistics =
        # ==============

        await self._test_eeprom_statistics(
            settings.stu.production_date,
            settings.stu.batch_number,
        )

        # =================
        # = EEPROM Status =
        # =================

        await self._test_eeprom_status()


# -- Main ---------------------------------------------------------------------


def main():
    """Run production test for Stationary Transceiver Unit (STU)"""

    unittest_main(
        testRunner=ExtendedTestRunner, module="icotronic.test.production.stu"
    )


if __name__ == "__main__":
    main()
