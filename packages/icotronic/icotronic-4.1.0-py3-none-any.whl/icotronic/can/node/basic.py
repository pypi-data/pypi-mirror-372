"""Communicate and control an ICOtronic node"""

# -- Imports ------------------------------------------------------------------

from __future__ import annotations

from semantic_version import Version

from icotronic.can.node.eeprom.node import NodeEEPROM
from icotronic.can.node.id import NodeId
from icotronic.can.node.spu import SPU
from icotronic.can.protocol.message import Message
from icotronic.can.status import State
from icotronic.utility.data import convert_bytes_to_text

# -- Classes ------------------------------------------------------------------


class Node:
    """Contains functionality shared by STU and sensor nodes

    Args:

        spu:
            The SPU object used to communicate with the node

        eeprom:
            The EEPROM class of the node

        id:
            The node identifier for the node

    """

    def __init__(
        self, spu: SPU, eeprom_class: type[NodeEEPROM], node_id: NodeId
    ) -> None:

        self.spu = spu
        self.id = node_id
        self.eeprom = eeprom_class(spu, node_id)

    # ==========
    # = System =
    # ==========

    async def reset(self) -> None:
        """Reset the node

        Examples:

            Import required library code

            >>> from asyncio import run, sleep
            >>> from icotronic.can.connection import Connection

            Reset the current STU

            >>> async def reset():
            ...     async with Connection() as stu:
            ...         await stu.reset()
            >>> run(reset())

            Reset a sensor node

            >>> async def reset():
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0) as sensor_node:
            ...             await sensor_node.reset()
            ...             # Wait some time for reset to take place
            ...             await sleep(1)
            >>> run(reset())

        """

        node = self.id
        message = Message(
            block="System",
            block_command="Reset",
            sender=self.spu.id,
            receiver=node,
            request=True,
        )
        await self.spu.request(
            message,
            description=f"reset node “{node}”",
            response_data=message.data,
            minimum_timeout=1,
        )

    # -----------------
    # - Get/Set State -
    # -----------------

    async def get_state(self) -> State:
        """Get the current state of the node

        Returns:

            The state of the node

        Examples:

            Import required library code

            >>> from asyncio import run, sleep
            >>> from icotronic.can.connection import Connection

            Get the state of the current STU

            >>> async def get_state():
            ...     async with Connection() as stu:
            ...         return await stu.get_state()
            >>> run(get_state())
            Get State, Location: Application, State: Operating

            Get state of sensor node

            >>> async def get_state():
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         async with stu.connect_sensor_node(0) as sensor_node:
            ...             state = await sensor_node.get_state()
            ...             # Sensor node might be still in startup state
            ...             while state.state_name() == 'Startup':
            ...                 await sleep(1)
            ...                 state = await sensor_node.get_state()
            ...             return state
            >>> run(get_state())
            Get State, Location: Application, State: Operating

        """

        node = self.id
        message = Message(
            block="System",
            block_command="Get/Set State",
            sender=self.spu.id,
            receiver=node,
            request=True,
            data=[(State(mode="Get")).value],
        )

        response = await self.spu.request(
            message, description=f"get state of node “{node}”"
        )

        return State(response.data[0])

    # ================
    # = Product Data =
    # ================

    async def get_gtin(self) -> int:
        """Retrieve the GTIN (Global Trade Identification Number) of the node

        Returns:

            The Global Trade Identification Number

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the GTIN of STU 1

            >>> async def read_gtin():
            ...     async with Connection() as stu:
            ...         return await stu.get_gtin()
            >>> gtin = run(read_gtin())
            >>> isinstance(gtin, int)
            True

        """

        node = self.id
        response = await self.spu.request_product_data(
            node=node,
            description=f"read GTIN of node “{node}”",
            block_command="GTIN",
        )

        return int.from_bytes(response.data, byteorder="little")

    async def get_hardware_version(self) -> Version:
        """Retrieve the hardware version of a node

        Returns:

            The hardware version of the node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the hardware version of STU 1

            >>> async def read_hardware_version():
            ...     async with Connection() as stu:
            ...         return await stu.get_hardware_version()
            >>> hardware_version = run(read_hardware_version())
            >>> hardware_version.major
            1

        """

        node = self.id
        response = await self.spu.request_product_data(
            node=node,
            description=f"read hardware version of node “{node}”",
            block_command="Hardware Version",
        )

        major, minor, patch = response.data[-3:]
        return Version(major=major, minor=minor, patch=patch)

    async def get_firmware_version(self) -> Version:
        """Retrieve the firmware version of the node

        Returns:

            The firmware version of the node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the firmware version of STU 1

            >>> async def read_firmware_version():
            ...     async with Connection() as stu:
            ...         return await stu.get_firmware_version()
            >>> firmware_version = run(read_firmware_version())
            >>> firmware_version.major
            2

        """

        node = self.id
        response = await self.spu.request_product_data(
            node=node,
            description=f"read firmware version of node “{node}”",
            block_command="Firmware Version",
        )

        major, minor, patch = response.data[-3:]
        return Version(major=major, minor=minor, patch=patch)

    async def get_firmware_release_name(self) -> str:
        """Retrieve the firmware release name of a node

        Returns:

            The firmware release name of the specified node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the firmware release name of STU 1

            >>> async def read_release_name():
            ...     async with Connection() as stu:
            ...         return await stu.get_firmware_release_name()
            >>> run(read_release_name())
            'Valerie'

        """

        node = self.id
        response = await self.spu.request_product_data(
            node=node,
            description=f"read firmware release name of node “{node}”",
            block_command="Release Name",
        )

        release_name = convert_bytes_to_text(response.data, until_null=True)
        return release_name

    async def get_serial_number(self) -> str:
        """Retrieve the serial number of a node

        Returns:

            The serial number of the node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the serial number of STU 1

            >>> async def read_serial_number():
            ...     async with Connection() as stu:
            ...         return await stu.get_serial_number()
            >>> serial_number = run(read_serial_number())
            >>> isinstance(serial_number, str)
            True
            >>> 0 <= len(serial_number) <= 32
            True

        """

        async def get_serial_number_part(part: int) -> bytearray:
            """Retrieve a part of the serial number"""
            node = self.id
            response = await self.spu.request_product_data(
                node=node,
                description=(
                    f"read part {part} of the serial number of node “{node}”"
                ),
                block_command=f"Serial Number {part}",
            )
            return response.data

        serial_number_bytes = bytearray()
        for part in range(1, 5):
            serial_number_bytes.extend(await get_serial_number_part(part))

        return convert_bytes_to_text(serial_number_bytes)

    async def get_product_name(self) -> str:
        """Retrieve the product name of a node

        Returns:

            The product name of the node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the product name of STU 1

            >>> async def read_product_name():
            ...     async with Connection() as stu:
            ...         return await stu.get_product_name()
            >>> product_name = run(read_product_name())
            >>> isinstance(product_name, str)
            True
            >>> 0 <= len(product_name) <= 128
            True

        """

        async def get_product_name_part(part: int) -> bytearray:
            """Retrieve a part of the product name"""

            node = self.id
            response = await self.spu.request_product_data(
                node=node,
                description=(
                    f"read part {part} of the product name of node “{node}”"
                ),
                block_command=f"Product Name {part}",
            )
            return response.data

        product_name_bytes = bytearray()
        for part in range(1, 17):
            product_name_bytes.extend(await get_product_name_part(part))

        return convert_bytes_to_text(product_name_bytes)

    async def get_oem_data(self) -> bytearray:
        """Retrieve the OEM (free use) data

        Returns:

            The OEM data of the node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Read the OEM data of STU 1

            >>> async def read_oem_data():
            ...     async with Connection() as stu:
            ...         return await stu.get_oem_data()
            >>> oem_data = run(read_oem_data())
            >>> isinstance(oem_data, bytearray)
            True
            >>> len(oem_data)
            64

        """

        async def get_oem_part(part: int) -> bytearray:
            """Retrieve a part of the OEM data"""
            node = self.id
            response = await self.spu.request_product_data(
                node=node,
                description=(
                    f"read part {part} of the OEM data of node “{node}”"
                ),
                block_command=f"OEM Free Use {part}",
            )
            return response.data

        oem_data = bytearray()
        for part in range(1, 9):
            oem_data.extend(await get_oem_part(part))

        return oem_data


# -- Main ---------------------------------------------------------------------

if __name__ == "__main__":
    from doctest import run_docstring_examples

    run_docstring_examples(
        Node.get_state,
        globals(),
        verbose=True,
    )
