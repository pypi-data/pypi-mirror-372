"""Define block and block commands for the ICOtronic system

See also: https://mytoolit.github.io/Documentation/#blocks
"""

# -- Classes ------------------------------------------------------------------


class UnknownBlockCommandError(Exception):
    """Raised if the block command is undefined/unknown"""


class UnknownBlockError(Exception):
    """Raised if the block is undefined/unknown"""


# pylint: disable=too-few-public-methods


class CANIdPart:
    """Stores data for a part of the CAN identifier

    Args:

        number:
            The value of the CAN identifier part

        name:
            The name of the CAN identifier part

        description:
            A short description of the CAN identifier part

    """

    def __init__(self, number: int, name: str, description: str) -> None:

        self.number = number
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        """Get the string representation of the CAN identifier part

        Examples:

            Get the textual representation of example CAN identifier info

            >>> CANIdPart(0x01, "Reset", "System Command Reset")
            Reset (0x01): System Command Reset

            >>> CANIdPart(0x80, "Energy", "Statistical Data Command Energy")
            Energy (0x80): Statistical Data Command Energy

        Returns:

            A string representing the CAN identifier part

        """

        return f"{self.name} (0x{self.number:02X}): {self.description}"


class Block(CANIdPart):
    """Store information about a block including its block commands

    Args:

        number:
            The value of the CAN identifier part

        name:
            The name of the CAN identifier part

        description:
            A short description of the CAN identifier part

        block_commands:
            The list of block commands contained in this block

    """

    def __init__(
        self,
        number: int,
        name: str,
        description: str,
        block_commands: list[CANIdPart],
    ) -> None:

        super().__init__(number, name, description)
        self.block_commands: dict[int | str, CANIdPart] = {}
        for block_command in block_commands:
            self.block_commands[block_command.number] = block_command
            self.block_commands[block_command.name] = block_command

    def __getitem__(self, block_command: int | str) -> CANIdPart:
        """Get the block command with the specified number or name

        Args:

            block_command:
                The name or number of the block command

        Returns:

            The requested block command

        Raises:

            UnknownBlockCommandError
                if the command block is not part of the block

        Examples:

            Get block command by number

            >>> block = Block(
            ...     0x00,
            ...     "System",
            ...     "Command Block System",
            ...     [
            ...         CANIdPart(0x00, "Verboten", "System Command Verboten"),
            ...         CANIdPart(0x01, "Reset", "System Command Reset"),
            ...     ],
            ... )
            >>> block[0]
            Verboten (0x00): System Command Verboten
            >>> block[0] == block["Verboten"]
            True

            Accessing a non existent block command should fail

            >>> block[-1] # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
                ...
            UnknownBlockCommandError: Unknown block command: “-1”

        """

        try:
            return self.block_commands[block_command]
        except KeyError as error:
            raise UnknownBlockCommandError(
                f"Unknown block command: “{block_command}”"
            ) from error


class Blocks:
    """Store information about available blocks

    Args:

        block_info:
            A list containing each block

    """

    def __init__(self, block_info: list[Block]):

        self.blocks: dict[int | str, Block] = {}
        for block in block_info:
            self.blocks[block.number] = block
            self.blocks[block.name] = block

    def __getitem__(self, block: int | str) -> Block:
        """Get the block with the specified number or name

        Args:

            block:
                The name or number of the block

        Returns:

            The requested block

        Raises:

            UnknownBlockCommandError:
                if the command block is not part of the block

        Examples:

            Create a Blocks object

            >>> blocks = Blocks([
            ...     Block(
            ...         0x00,
            ...         "System",
            ...         "Command Block System",
            ...         [
            ...             CANIdPart(0x00, "Verboten",
            ...                       "System Command Verboten"),
            ...             CANIdPart(0x01, "Reset", "System Command Reset"),
            ...         ],
            ... )])

            Retrieve an existing block

            >>> blocks["System"]
            System (0x00): Command Block System

            Retrieving an non-existing block will fail

            >>> blocks["Does Not Exist"] # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
                ...
            UnknownBlockError: Unknown block: “Does Not Exist”

        """

        try:
            return self.blocks[block]
        except KeyError as error:
            raise UnknownBlockError(f"Unknown block: “{block}”") from error

    def __repr__(self) -> str:
        """Get the string representation of the blocks

        Returns:

            The string representation of the stored blocks

        Examples:

            Get the textual representation of a Blocks object

            >>> Blocks([
            ...     Block(
            ...         0x3F,
            ...         "Test",
            ...         "Command Block Test",
            ...         [
            ...             CANIdPart(0x01, "Signal", "Test Command Signal"),
            ...             CANIdPart(0x69, "Pfeifferl",
            ...                       "Test Command Pfeifferl"),
            ...         ]
            ...     ),
            ...     Block(0x3E, "Product Data",
            ...           "Command Block Product Data", [])
            ... ]) # doctest: +NORMALIZE_WHITESPACE
            [Test (0x3F): Command Block Test,
             Product Data (0x3E): Command Block Product Data]

        """

        return (
            "["
            + ", ".join([
                repr(block)
                for name, block in self.blocks.items()
                if isinstance(name, str)
            ])
            + "]"
        )


# pylint: enable=too-few-public-methods

blocks = Blocks([
    Block(
        0x00,
        "System",
        "Command Block System",
        [
            CANIdPart(0x00, "Verboten", "System Command Verboten"),
            CANIdPart(0x01, "Reset", "System Command Reset"),
            CANIdPart(0x02, "Get/Set State", "System Command Get/Set State"),
            CANIdPart(0x03, "Mode", "System Command Mode"),
            CANIdPart(0x04, "Alarm", "System Command Alarm"),
            CANIdPart(0x05, "Node Status", "System Command Status Word0"),
            CANIdPart(0x06, "Error Status", "System Command Status Word1"),
            CANIdPart(0x07, "StatusWord2", "System Command Status Word2"),
            CANIdPart(0x08, "StatusWord3", "System Command Status Word3"),
            CANIdPart(0x09, "Test", "System Command Test"),
            CANIdPart(0x0A, "Log", "System Command Log"),
            CANIdPart(0x0B, "Bluetooth", "System Command BlueTooth"),
            CANIdPart(0x0C, "Routing", "System Command Routing"),
        ],
    ),
    Block(
        0x04,
        "Streaming",
        "Command Block Streaming",
        [
            CANIdPart(0x00, "Data", "Streaming Command Data"),
            CANIdPart(0x01, "Temperature", "Streaming Command Temperature"),
            CANIdPart(0x20, "Voltage", "Streaming Command Voltage"),
            CANIdPart(0x40, "Current", "Streaming Command Current"),
        ],
    ),
    Block(
        0x08,
        "StatisticalData",
        "Command Block Statistical Data",
        [
            CANIdPart(
                0x00,
                "PowOnOff",
                "Statistical Data Command PowerOn/Off Counter",
            ),
            CANIdPart(
                0x01,
                "OperatingTime",
                "Statistical Data Command Operating Time",
            ),
            CANIdPart(
                0x02, "UVC", "Statistical Data Command Under-Voltage Counter"
            ),
            CANIdPart(
                0x03, "WDog", "Statistical Data Command Watchdog Counter"
            ),
            CANIdPart(
                0x04,
                "ProductionDate",
                "Statistical Data Command Production Date",
            ),
            CANIdPart(
                0x40,
                "MeasurementInterval",
                "Statistical Data Command Measurement Interval",
            ),
            CANIdPart(
                0x41,
                "QuantityInterval",
                "Statistical Data Command Quantity Interval",
            ),
            CANIdPart(0x80, "Energy", "Statistical Data Command Energy"),
        ],
    ),
    Block(
        0x28,
        "Configuration",
        "Command Block Configuration",
        [
            CANIdPart(
                0x00,
                "Get/Set ADC Configuration",
                "Configuration Command Acceleration Configuration",
            ),
            CANIdPart(
                0x01,
                "Channel Configuration",
                "Configuration Command Channel Configuration",
            ),
            CANIdPart(
                0x20, "Voltage", "Configuration Command Voltage Configuration"
            ),
            CANIdPart(
                0x40, "Current", "Configuration Command Current Configuration"
            ),
            CANIdPart(
                0x60,
                "CalibrationFactorK",
                "Configuration Command Calibration Factor K",
            ),
            CANIdPart(
                0x61,
                "CalibrationFactorD",
                "Configuration Command Calibration Factor D",
            ),
            CANIdPart(
                0x62,
                "Calibration Measurement",
                "Configuration Command Calibration Measurement",
            ),
            CANIdPart(0x80, "Alarm", "Configuration Command Alarm"),
            CANIdPart(0xC0, "HMI", "Configuration Command HMI"),
        ],
    ),
    Block(
        0x3D,
        "EEPROM",
        "Command Block EEPROM",
        [
            CANIdPart(0x00, "Read", "EEPROM Command Read"),
            CANIdPart(0x01, "Write", "EEPROM Command Write"),
            CANIdPart(
                0x20,
                "Read Write Request Counter",
                "EEPROM Command Write Request Counter",
            ),
        ],
    ),
    Block(
        0x3E,
        "Product Data",
        "Command Block Product Data",
        [
            CANIdPart(0x00, "GTIN", "Product Data Command GTIN"),
            CANIdPart(
                0x01,
                "Hardware Version",
                "Product Data Command Hardware Version",
            ),
            CANIdPart(
                0x02,
                "Firmware Version",
                "Product Data Command Firmware Version",
            ),
            CANIdPart(
                0x03, "Release Name", "Product Data Command Release Name"
            ),
            CANIdPart(
                0x04, "Serial Number 1", "Product Data Command Serial Number 1"
            ),
            CANIdPart(
                0x05, "Serial Number 2", "Product Data Command Serial Number 2"
            ),
            CANIdPart(
                0x06, "Serial Number 3", "Product Data Command Serial Number 3"
            ),
            CANIdPart(
                0x07, "Serial Number 4", "Product Data Command Serial Number 4"
            ),
            CANIdPart(0x08, "Product Name 1", "Product Data Command Name1"),
            CANIdPart(0x09, "Product Name 2", "Product Data Command Name2"),
            CANIdPart(0x0A, "Product Name 3", "Product Data Command Name3"),
            CANIdPart(0x0B, "Product Name 4", "Product Data Command Name4"),
            CANIdPart(0x0C, "Product Name 5", "Product Data Command Name5"),
            CANIdPart(0x0D, "Product Name 6", "Product Data Command Name6"),
            CANIdPart(0x0E, "Product Name 7", "Product Data Command Name7"),
            CANIdPart(0x0F, "Product Name 8", "Product Data Command Name8"),
            CANIdPart(0x10, "Product Name 9", "Product Data Command Name9"),
            CANIdPart(0x11, "Product Name 10", "Product Data Command Name10"),
            CANIdPart(0x12, "Product Name 11", "Product Data Command Name11"),
            CANIdPart(0x13, "Product Name 12", "Product Data Command Name12"),
            CANIdPart(0x14, "Product Name 13", "Product Data Command Name13"),
            CANIdPart(0x15, "Product Name 14", "Product Data Command Name14"),
            CANIdPart(0x16, "Product Name 15", "Product Data Command Name15"),
            CANIdPart(0x17, "Product Name 16", "Product Data Command Name16"),
            CANIdPart(
                0x18, "OEM Free Use 1", "Product Data Command Free Use 1"
            ),
            CANIdPart(
                0x19, "OEM Free Use 2", "Product Data Command Free Use 2"
            ),
            CANIdPart(
                0x1A, "OEM Free Use 3", "Product Data Command Free Use 3"
            ),
            CANIdPart(
                0x1B, "OEM Free Use 4", "Product Data Command Free Use 4"
            ),
            CANIdPart(
                0x1C, "OEM Free Use 5", "Product Data Command Free Use 5"
            ),
            CANIdPart(
                0x1D, "OEM Free Use 6", "Product Data Command Free Use 6"
            ),
            CANIdPart(
                0x1E, "OEM Free Use 7", "Product Data Command Free Use 7"
            ),
            CANIdPart(
                0x1F, "OEM Free Use 8", "Product Data Command Free Use 8"
            ),
        ],
    ),
    Block(
        0x3F,
        "Test",
        "Command Block Test",
        [
            CANIdPart(0x01, "Signal", "Test Command Signal"),
            CANIdPart(0x69, "Pfeifferl", "Test Command Pfeifferl"),
        ],
    ),
])
"""MyTooliT Protocol command blocks

See also: https://mytoolit.github.io/Documentation/#blocks
"""

# -- Main ---------------------------------------------------------------------

if __name__ == "__main__":
    from doctest import testmod

    testmod()
