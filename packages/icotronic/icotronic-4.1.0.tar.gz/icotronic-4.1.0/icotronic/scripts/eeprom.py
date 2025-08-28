"""Check EEPROM of ICOtronic node"""

# -- Imports ------------------------------------------------------------------

from argparse import ArgumentParser, Namespace
from asyncio import run
from collections import Counter

from icotronic.can import Connection
from icotronic.cmdline.parse import byte_value, mac_address

# -- Function -----------------------------------------------------------------


def parse_arguments() -> Namespace:
    """Parse the arguments of the EEPROM checker command line tool

    Returns:

        A simple object storing the MAC address (attribute ``mac``) of an STH
        and an byte value that should be stored into the cells of the EEPROM
        (attribute ``value``)

    """

    parser = ArgumentParser(
        description="Check the integrity of STH EEPROM content"
    )
    parser.add_argument(
        "mac",
        help="MAC address of STH e.g. 08:6b:d7:01:de:81",
        type=mac_address,
    )
    parser.add_argument(
        "--value",
        help="byte value for EEPROM cells (default: %(default)s)",
        type=byte_value,
        default=10,
    )

    return parser.parse_args()


# -- Class --------------------------------------------------------------------


class EEPROMCheck:
    """Write and check the content of a sensor node EEPROM page

    Args:

        sensor_node:
            The sensor node where the EEPROM check should take place

        value:
            The value that the EEPROM checker should write into the EEPROM

    """

    def __init__(self, sensor_node, value):

        self.sensor_node = sensor_node
        self.eeprom_address = 1
        self.eeprom_length = 256
        self.eeprom_value = value

    async def write_eeprom(self):
        """Write a byte value into one page of the EEPROM"""

        print(f"Write value “{self.eeprom_value}” into EEPROM cells")
        await self.sensor_node.eeprom.write(
            address=1,
            offset=0,
            data=[self.eeprom_value for _ in range(self.eeprom_length)],
        )

    async def read_eeprom(self):
        """Read a page of the EEPROM

        Returns:

            A list of the byte values stored in the EEPROM page

        """

        return await self.sensor_node.eeprom.read(
            address=self.eeprom_address,
            offset=0,
            length=self.eeprom_length,
        )

    async def print_eeprom_incorrect(self):
        """Print a summary of the incorrect values in the EEPROM page"""

        changed = [
            byte
            for byte in await self.read_eeprom()
            if byte != self.eeprom_value
        ]
        incorrect = len(changed) / self.eeprom_length
        counter = Counter(changed)
        summary = ", ".join(
            f"{value} ({times} time{'' if times == 1 else 's'})"
            for value, times in sorted(
                counter.items(), key=lambda item: item[1], reverse=True
            )
        )
        print(f"{incorrect:.2%} incorrect{': ' if summary else ''}{summary}")

    async def print_eeprom(self):
        """Print the values stored in the EEPROM page"""

        page = await self.read_eeprom()
        bytes_per_line = 8
        for byte in range(0, self.eeprom_length - 1, bytes_per_line):
            print(f"{byte:3}: ", end="")
            byte_representation = " ".join(["{:3}"] * bytes_per_line).format(
                *page[byte : byte + bytes_per_line]
            )
            print(byte_representation)


# -- Functions ----------------------------------------------------------------


async def check_eeprom(arguments: Namespace):
    """Check EEPROM functionality

    Args:

        arguments:
            Command line arguments

    """

    times = 5

    async with Connection() as stu:
        async with stu.connect_sensor_node(arguments.mac) as sensor_node:
            print(f"Connected to node “{await sensor_node.get_name()}”")
            check = EEPROMCheck(sensor_node, arguments.value)
            await check.write_eeprom()
            await check.print_eeprom_incorrect()
            print()
        for counter in range(times):
            async with stu.connect_sensor_node(arguments.mac) as sensor_node:
                check = EEPROMCheck(sensor_node, arguments.value)
                await check.print_eeprom_incorrect()
                print()
                if counter >= times - 1:
                    await check.print_eeprom()


# -- Main ---------------------------------------------------------------------


def main():
    """Check EEPROM of node specified via command line argument"""
    run(check_eeprom(parse_arguments()))


if __name__ == "__main__":
    main()
