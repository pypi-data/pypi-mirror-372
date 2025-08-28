"""Read name of sensor node with node number 0"""

# -- Imports ------------------------------------------------------------------

from asyncio import run

from netaddr import EUI

from icotronic.can import Connection

# -- Functions ----------------------------------------------------------------


async def read_name(identifier: EUI | str | int) -> None:
    """Read sensor node name

    Args:

        identifier:

            Identifier of STH node

    """

    async with Connection() as stu:
        async with stu.connect_sensor_node(identifier) as sensor_node:
            name = await sensor_node.get_name()
            print(f"Connected to sensor node “{name}”")


# -- Main ---------------------------------------------------------------------

if __name__ == "__main__":
    # Possible Identifiers:
    # - Name:               e.g. `"Test-STH"`
    # - Sensor Node Number: e.g. `1`
    # - MAC Address:        e.g. `netaddr.EUI('08-6B-D7-01-DE-81')`
    run(read_name(identifier=0))
