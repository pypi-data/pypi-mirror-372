"""Support for communicating with the Stationary Transceiver Unit (STU)"""

# -- Imports ------------------------------------------------------------------

from __future__ import annotations

from argparse import ArgumentTypeError
from asyncio import sleep
from time import monotonic
from types import TracebackType
from typing import NamedTuple

from netaddr import EUI

from icotronic.cmdline.parse import (
    node_name as check_name,
    sensor_node_number as check_sensor_node_number,
)
from icotronic.can.constants import SENSOR_NODE_NUMBER_SELF_ADDRESSING
from icotronic.can.node.eeprom.node import NodeEEPROM
from icotronic.can.error import ErrorResponseError, NoResponseError
from icotronic.can.node.basic import Node
from icotronic.can.node.id import NodeId
from icotronic.can.node.sensor import SensorNode
from icotronic.can.node.spu import SPU
from icotronic.utility.data import convert_bytes_to_text

# -- Classes ------------------------------------------------------------------


class AsyncSensorNodeManager:
    """Context manager for connection to sensor node

    Args:

        stu:
            The STU instance that created the context manager

        identifier:
            The identifier of the sensor node

        sensor_node_class:
            The sensor node class returned by the context manager

    Raises:

        ValueError:
             If you use an invalid name or node number as identifier

    """

    def __init__(
        self,
        stu: STU,
        identifier: int | str | EUI,
        sensor_node_class: type[SensorNode] = SensorNode,
    ) -> None:

        try:
            if isinstance(identifier, int):
                check_sensor_node_number(str(identifier))
            elif isinstance(identifier, str):
                check_name(identifier)
        except ArgumentTypeError as error:
            raise ValueError(error) from error

        self.stu = stu
        self.identifier = identifier
        self.sensor_node_class = sensor_node_class

    async def __aenter__(self) -> SensorNode:
        """Create the connection to the sensor node"""

        def get_sensor_node(
            nodes: list[SensorNodeInfo], identifier: int | str | EUI
        ) -> SensorNodeInfo | None:
            """Get the MAC address of a sensor node"""

            for node in nodes:
                if (  # pylint: disable=too-many-boolean-expressions
                    isinstance(identifier, str)
                    and node.name == identifier
                    or isinstance(identifier, int)
                    and node.sensor_node_number == identifier
                    or isinstance(identifier, EUI)
                    and node.mac_address == identifier
                ):
                    return node

            return None

        await self.stu.activate_bluetooth()

        # We wait for a certain amount of time for the connection to the
        # node to take place
        timeout_in_s = 20
        end_time = monotonic() + timeout_in_s

        sensor_node = None
        sensor_nodes: list[SensorNodeInfo] = []
        while sensor_node is None:
            if monotonic() > end_time:
                sensor_nodes_representation = "\n".join(
                    [repr(node) for node in sensor_nodes]
                )
                node_info = (
                    "Found the following sensor nodes:\n"
                    f"{sensor_nodes_representation}"
                    if len(sensor_nodes) > 0
                    else "No sensor nodes found"
                )

                identifier_description = (
                    "MAC address"
                    if isinstance(self.identifier, EUI)
                    else (
                        "sensor_node_number"
                        if isinstance(self.identifier, int)
                        else "name"
                    )
                )
                raise TimeoutError(
                    "Unable to find sensor node with "
                    f"{identifier_description} “{self.identifier}” in "
                    f"{timeout_in_s} seconds\n\n{node_info}"
                )

            sensor_nodes = await self.stu.get_sensor_nodes()
            sensor_node = get_sensor_node(sensor_nodes, self.identifier)
            if sensor_node is None:
                await sleep(0.1)

        connection_attempt_time = monotonic()
        disconnected = True
        while disconnected:
            await self.stu.connect_with_number(sensor_node.sensor_node_number)
            retry_time_s = 3
            end_time_retry = monotonic() + retry_time_s
            while monotonic() < end_time_retry:
                if monotonic() > end_time:
                    connection_time = monotonic() - connection_attempt_time
                    raise TimeoutError(
                        "Unable to connect to sensor node"
                        f" “{sensor_node}” in"
                        f" {connection_time:.3f} seconds"
                    )

                if await self.stu.is_connected():
                    disconnected = False
                    break

                await sleep(0.1)

        return self.sensor_node_class(self.stu.spu)

    async def __aexit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Disconnect the sensor node and clean up resources

        Args:

            exception_type:
                The type of the exception in case of an exception

            exception_value:
                The value of the exception in case of an exception

            traceback:
                The traceback in case of an exception

        """

        try:
            await self.stu.deactivate_bluetooth()
        except (NoResponseError, ErrorResponseError):
            pass


class SensorNodeInfo(NamedTuple):
    """Used to store information about a (disconnected) STH"""

    name: str
    """The (Bluetooth advertisement) name of the STH"""

    sensor_node_number: int
    """The node number of the STH"""

    mac_address: EUI
    """The (Bluetooth) MAC address of the STH"""

    rssi: int
    """The RSSI of the STH"""

    def __repr__(self) -> str:
        """Return the string representation of an STH

        Returns:

            A textual representation of the sensor node information

        """

        attributes = ", ".join([
            f"Name: {self.name}",
            f"Number: {self.sensor_node_number}",
            f"MAC Address: {self.mac_address}",
            f"RSSI: {self.rssi}",
        ])
        return f"🤖 {attributes}"

    def __hash__(self):
        """Calculate hash value

        Note:

            This function is required in addition to ``__eq__`` to be
            able to put sensor node information into a set.

        Returns:

            The hash value of the sensor device information

        Examples:

            Update old information about sensor devices with new information

            >>> sensor_node_1 = SensorNodeInfo(
            ...                     name="Test-STH",
            ...                     sensor_node_number=1,
            ...                     mac_address=EUI("08-6B-D7-01-DE-81"),
            ...                     rssi=-58 )
            >>> sensor_node_2 = SensorNodeInfo(
            ...                     name="Test-STH",
            ...                     sensor_node_number=2,
            ...                     mac_address=EUI("08-6B-D7-01-DE-81"),
            ...                     rssi=-80)
            >>> sensor_node_3 = SensorNodeInfo(
            ...                     name="Something",
            ...                     sensor_node_number=3,
            ...                     mac_address=EUI("12-34-56-78-9A-BC"),
            ...                     rssi=-80)

            >>> old = {sensor_node_1, sensor_node_3}
            >>> new = {sensor_node_2, sensor_node_3}
            >>> new | old == {sensor_node_2, sensor_node_3}
            True

        """

        return hash(self.mac_address)

    def __eq__(self, other: object) -> bool:
        """Compare two sensor nodes for equality

        Args:

            other:
                The object this sensor node (information) should be compared
                to

        Returns:

            - ``True`` if the sensor nodes share the same name and MAC address,
              or
            - ``False`` otherwise

        Examples:

            Compare two sensor nodes, which are considered equal

            >>> sensor_node_1 = SensorNodeInfo(
            ...                     name="Test-STH",
            ...                     sensor_node_number=1,
            ...                     mac_address=EUI("08-6B-D7-01-DE-81"),
            ...                     rssi=-58 )
            >>> sensor_node_2 = SensorNodeInfo(
            ...                     name="Test-STH",
            ...                     sensor_node_number=2,
            ...                     mac_address=EUI("08-6B-D7-01-DE-81"),
            ...                     rssi=-80)
            >>> sensor_node_1 == sensor_node_2
            True

            Compare two sensor nodes, which are not considered equal

            >>> sensor_node_3 = SensorNodeInfo(
            ...                     name="Something",
            ...                     sensor_node_number=3,
            ...                     mac_address=EUI("12-34-56-78-9A-BC"),
            ...                     rssi=-80)
            >>> sensor_node_2 == sensor_node_3
            False

        """

        if not isinstance(other, type(self)):
            return NotImplemented

        return self.mac_address == other.mac_address


class STU(Node):
    """Communicate and control a connected STU

    Args:

        spu:
            The SPU object that created this STU instance

    Examples:

        Import required library code

        >>> from asyncio import run
        >>> from icotronic.can.connection import Connection

        Create an STU object

        >>> async def create_stu():
        ...     async with Connection() as stu:
        ...         pass # call some coroutines of `stu` object
        >>> run(create_stu())

    """

    def __init__(self, spu: SPU) -> None:

        super().__init__(spu, NodeEEPROM, NodeId("STU 1"))

    async def activate_bluetooth(self) -> None:
        """Activate Bluetooth on the STU

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Activate Bluetooth on the STU

            >>> async def activate():
            ...     async with Connection() as stu:
            ...         await stu.activate_bluetooth()
            >>> run(activate())

        """

        await self.spu.request_bluetooth(
            node=self.id,
            subcommand=1,
            description=f"activate Bluetooth of node “{self.id}”",
            response_data=6 * [0],  # type: ignore[arg-type]
        )

    async def deactivate_bluetooth(self) -> None:
        """Deactivate Bluetooth on the STU

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Deactivate Bluetooth on STU 1

            >>> async def deactivate_bluetooth():
            ...     async with Connection() as stu:
            ...         await stu.deactivate_bluetooth()
            >>> run(deactivate_bluetooth())

        """

        await self.spu.request_bluetooth(
            node=self.id,
            subcommand=9,
            description=f"deactivate Bluetooth on “{self.id}”",
            response_data=6 * [0],  # type: ignore[arg-type]
        )

    async def get_available_nodes(self) -> int:
        """Retrieve the number of available sensor nodes

        Returns:

            The number of available sensor nodes

        Examples:

            Import required library code

            >>> from asyncio import run, sleep
            >>> from icotronic.can.connection import Connection

            Get the number of available Bluetooth nodes at STU 1

            >>> async def get_number_bluetooth_nodes():
            ...     async with Connection() as stu:
            ...         await stu.activate_bluetooth()
            ...
            ...         # We assume at least one STH is available
            ...         number_sths = 0
            ...         while number_sths <= 0:
            ...             number_sths = await stu.get_available_nodes()
            ...             await sleep(0.1)
            ...
            ...         return number_sths
            >>> run(get_number_bluetooth_nodes()) >= 0
            1

        """

        answer = await self.spu.request_bluetooth(
            node=self.id,
            subcommand=2,
            description=f"get available Bluetooth nodes of node “{self.id}”",
        )

        available_nodes = int(convert_bytes_to_text(answer.data[2:]))

        return available_nodes

    async def get_name(
        self, sensor_node_number: int = SENSOR_NODE_NUMBER_SELF_ADDRESSING
    ) -> str:
        """Retrieve the name of a sensor node

        Args:

            sensor_node_number:
                The number of the Bluetooth node (0 up to the number of
                available nodes - 1); Use the special node number
                ``SENSOR_NODE_NUMBER_SELF_ADDRESSING`` to retrieve the
                name of the STU itself.

        Note:

            You are probably only interested in the name of the STU itself
            (``SENSOR_NODE_NUMBER_SELF_ADDRESSING``), if you want to know the
            advertisement name of the STU in OTA (Over The Air) update mode
            for flashing a new firmware onto the STU.

        Returns:

            The (Bluetooth broadcast) name of the node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Get Bluetooth advertisement name of node “0” from STU 1

            >>> async def get_bluetooth_node_name():
            ...     async with Connection() as stu:
            ...         await stu.activate_bluetooth()
            ...         # We assume that at least one STH is available
            ...         return await stu.get_name(0)
            >>> name = run(get_bluetooth_node_name())
            >>> isinstance(name, str)
            True
            >>> 0 <= len(name) <= 8
            True

        """

        return await self.spu.get_name(
            node=self.id, sensor_node_number=sensor_node_number
        )

    async def connect_with_number(self, sensor_node_number: int = 0) -> bool:
        """Connect to a Bluetooth node using a node number

        Args:

            sensor_node_number:
                The number of the Bluetooth node (0 up to the number of
                available nodes - 1)

        Returns:

            - True, if

              1. in search mode,
              2. at least single node was found,
              3. no legacy mode,
              4. and scanning mode active

            - False, otherwise

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Connect to node “0”

            >>> async def connect_bluetooth_sensor_node_number():
            ...     async with Connection() as stu:
            ...         await stu.activate_bluetooth()
            ...         # We assume that at least one STH is available
            ...         connected = before = await stu.is_connected()
            ...         while not connected:
            ...             connected = await stu.connect_with_number(0)
            ...         await stu.deactivate_bluetooth()
            ...         after = await stu.is_connected()
            ...         # Return status of Bluetooth node connect response
            ...         return before, connected, after
            >>> run(connect_bluetooth_sensor_node_number())
            (False, True, False)

        """

        response = await self.spu.request_bluetooth(
            node=self.id,
            subcommand=7,
            sensor_node_number=sensor_node_number,
            description=f"connect to “{sensor_node_number}” from “{self.id}”",
        )

        return bool(response.data[2])

    async def connect_with_mac_address(self, mac_address: EUI) -> None:
        """Connect to a Bluetooth sensor node using its MAC address

        Args:

            mac_address:
                The MAC address of the sensor node

        Examples:

            Import required library code

            >>> from asyncio import run, sleep
            >>> from icotronic.can.connection import Connection

            Connect to a sensor node via its MAC address

            >>> async def get_bluetooth_mac():
            ...     async with Connection() as stu:
            ...         await stu.activate_bluetooth()
            ...         # Wait for Bluetooth activation to take place
            ...         await sleep(2)
            ...         return await stu.get_mac_address(0)
            >>> mac_address = run(get_bluetooth_mac())
            >>> mac_address != EUI(0)
            True

            >>> async def connect(mac_address):
            ...     async with Connection() as stu:
            ...         await stu.deactivate_bluetooth()
            ...         # We assume that at least one STH is available
            ...         connected = before = await stu.is_connected()
            ...         await stu.activate_bluetooth()
            ...         while not connected:
            ...             await stu.connect_with_mac_address(mac_address)
            ...             await sleep(0.1)
            ...             connected = await stu.is_connected()
            ...         await stu.deactivate_bluetooth()
            ...         after = await stu.is_connected()
            ...         # Return status of Bluetooth node connect response
            ...         return before, connected, after
            >>> run(connect(mac_address))
            (False, True, False)

        """

        mac_address_bytes_reversed = list(reversed(mac_address.packed))
        node = "STU 1"
        # The STU returns reversed MAC address once, probably after the
        # connection was established successfully.
        # Otherwise (before and after) connection took place it returns
        # zeroes all the time. This means the return values is not that
        # useful, e.g. for determining if the STH is connected or not.
        await self.spu.request_bluetooth(
            node=node,
            subcommand=18,
            data=mac_address_bytes_reversed,
            description=f"connect to node “{mac_address}” from “{node}”",
        )

    async def is_connected(self) -> bool:
        """Check if the STU is connected to a Bluetooth node

        Returns:

        - True, if a Bluetooth node is connected to the node
        - False, otherwise

        Examples:

            >>> from asyncio import run, sleep
            >>> from icotronic.can.connection import Connection

            Check connection of node “0” to STU

            >>> async def check_bluetooth_connection():
            ...     async with Connection() as stu:
            ...         await stu.activate_bluetooth()
            ...         await sleep(0.1)
            ...         connected_start = await stu.is_connected()
            ...
            ...         # We assume that at least one STH is available
            ...         await stu.connect_with_number(0)
            ...         # Wait for node connection
            ...         connected_between = False
            ...         while not connected_between:
            ...             connected_between = await stu.is_connected()
            ...             await sleep(0.1)
            ...             await stu.connect_with_number(0)
            ...
            ...         # Deactivate Bluetooth connection
            ...         await stu.deactivate_bluetooth()
            ...         # Wait until node is disconnected
            ...         await sleep(0.1)
            ...         connected_after = await stu.is_connected()
            ...
            ...         return (connected_start, connected_between,
            ...                 connected_after)
            >>> run(check_bluetooth_connection())
            (False, True, False)

        """

        response = await self.spu.request_bluetooth(
            node=self.id,
            subcommand=8,
            response_data=[None, *(5 * [0])],
            description=(
                f"check if “{self.id}” is connected to a Bluetooth node"
            ),
        )

        return bool(response.data[2])

    async def get_rssi(self, sensor_node_number: int):
        """Retrieve the RSSI (Received Signal Strength Indication) of an STH

        Args:

            sensor_node_number:
                The number of the Bluetooth node (0 up to the number of
                available nodes)

        Returns:

            The RSSI of the node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Retrieve the RSSI of a disconnected STH

            >>> async def get_bluetooth_rssi():
            ...     async with Connection() as stu:
            ...         await stu.activate_bluetooth()
            ...         # We assume that at least one STH is available
            ...         # Get the RSSI of node “0”
            ...         return await stu.get_rssi(0)
            >>> rssi = run(get_bluetooth_rssi())
            >>> -80 < rssi < 0
            True

        """

        return await self.spu.get_rssi(
            node=self.id, sensor_node_number=sensor_node_number
        )

    async def get_mac_address(
        self, sensor_node_number: int = SENSOR_NODE_NUMBER_SELF_ADDRESSING
    ) -> EUI:
        """Retrieve the MAC address of the STU or a sensor node

        Note:

            Bluetooth needs to be activated before calling this coroutine,
            otherwise an incorrect MAC address will be returned (for sensor
            nodes).

        Args:

            sensor_node_number:
                The node number of the Bluetooth node (0 up to the number of
                available nodes - 1) or ``0x00``
                (``SENSOR_NODE_NUMBER_SELF_ADDRESSING``) to retrieve the MAC
                address of the STU itself

        Returns:

            The MAC address of the specified sensor node

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Retrieve the MAC address of STH 1

            >>> async def get_bluetooth_mac():
            ...     async with Connection() as stu:
            ...         await stu.activate_bluetooth()
            ...         return await stu.get_mac_address(0)
            >>> mac_address = run(get_bluetooth_mac())
            >>> isinstance(mac_address, EUI)
            True
            >>> mac_address != EUI(0)
            True

        """

        return await self.spu.get_mac_address(self.id, sensor_node_number)

    async def get_sensor_nodes(self) -> list[SensorNodeInfo]:
        """Retrieve a list of available sensor nodes

        Returns:

            A list of available nodes including node number, name, MAC address
            and RSSI for each node

        Examples:

            Import required library code

            >>> from asyncio import run, sleep
            >>> from netaddr import EUI
            >>> from icotronic.can.connection import Connection

            Retrieve the list of Bluetooth nodes at STU 1

            >>> async def get_sensor_nodes():
            ...     async with Connection() as stu:
            ...         # We assume that at least one sensor node is available
            ...         nodes = []
            ...         while not nodes:
            ...             nodes = await stu.get_sensor_nodes()
            ...             await sleep(0.1)
            ...
            ...         return nodes
            >>> nodes = run(get_sensor_nodes())
            >>> len(nodes) >= 1
            True
            >>> node = nodes[0]

            >>> node.sensor_node_number
            0

            >>> isinstance(node.name, str)
            True
            >>> 0 <= len(node.name) <= 8
            True

            >>> -80 < node.rssi < 0
            True

            >>> isinstance(node.mac_address, EUI)
            True

        """

        await self.activate_bluetooth()
        available_nodes = await self.get_available_nodes()
        nodes = []
        for node in range(available_nodes):
            mac_address = await self.get_mac_address(node)
            rssi = await self.get_rssi(node)
            name = await self.get_name(node)

            nodes.append(
                SensorNodeInfo(
                    sensor_node_number=node,
                    mac_address=mac_address,
                    name=name,
                    rssi=rssi,
                )
            )

        return nodes

    async def collect_sensor_nodes(self, timeout=5) -> list[SensorNodeInfo]:
        """Collect available sensor nodes

        This coroutine collects sensor nodes until either

        - no new sensor node was found or
        - until the given timeout, if no sensor node was found.

        Args:

            timeout:

                The timeout in seconds until this coroutine returns, if no
                sensor node was found at all

        Returns:

            A list of found sensor nodes

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Collect available sensor nodes

            >>> async def collect_sensor_nodes():
            ...     async with Connection() as stu:
            ...         return await stu.collect_sensor_nodes()

            >>> # We assume that at least one sensor node is available
            >>> nodes = run(collect_sensor_nodes())
            >>> len(nodes) >= 1
            True

        """

        timeout = monotonic() + timeout
        sensor_nodes: set[SensorNodeInfo] = set()
        sensor_nodes_before: set[SensorNodeInfo] = set()

        # Wait
        # - until timeout, if there are no devices available or
        # - until no new devices have been found in an iteration of the loop
        while (
            len(sensor_nodes) <= 0
            and monotonic() < timeout
            or sensor_nodes != sensor_nodes_before
        ):
            sensor_nodes_before = set(sensor_nodes)
            sensor_nodes = (
                set(await self.get_sensor_nodes()) | sensor_nodes_before
            )
            await sleep(0.5)

        return list(sensor_nodes)

    def connect_sensor_node(
        self,
        identifier: int | str | EUI,
        sensor_node_class: type[SensorNode] = SensorNode,
    ) -> AsyncSensorNodeManager:
        """Connect to a sensor node (e.g. SHA, SMH or STH)

        Args:

            identifier:
                The

                - MAC address (`EUI`),
                - name (`str`), or
                - node number (`int`)

                of the sensor node we want to connect to

            sensor_node_class:
                Sensor node subclass that should be returned by context manager

        Returns:

            A context manager that returns a sensor node object for the
            connected node

        Raises:

            ValueError:
                 If you use an invalid name or node number as identifier

        Examples:

            Import required library code

            >>> from asyncio import run
            >>> from icotronic.can.connection import Connection

            Connect to the sensor node with node number ``0``

            >>> async def connect_sensor_node():
            ...     async with Connection() as stu:
            ...         async with stu.connect_sensor_node(0):
            ...             connected = await stu.is_connected()
            ...         after = await stu.is_connected()
            ...         return (connected, after)
            >>> run(connect_sensor_node())
            (True, False)

        """

        return AsyncSensorNodeManager(self, identifier, sensor_node_class)


# -- Main ---------------------------------------------------------------------

if __name__ == "__main__":
    from doctest import run_docstring_examples

    run_docstring_examples(
        STU.connect_with_mac_address,
        globals(),
        verbose=True,
    )
