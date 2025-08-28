"""Support for creating a connection to the ICOtronic system"""

# -- Imports ------------------------------------------------------------------

from __future__ import annotations

from asyncio import get_running_loop, to_thread
from sys import platform
from types import TracebackType

from can import Bus, BusABC, Notifier
from can.interfaces.pcan.pcan import PcanError

from icotronic.can.error import CANInitError
from icotronic.can.listener import Logger
from icotronic.can.node.spu import SPU
from icotronic.can.node.stu import STU
from icotronic.config import settings

# -- Classes ------------------------------------------------------------------


class Connection:
    """Basic class to initialize CAN communication

    To actually connect to the CAN bus you need to use the async context
    manager, provided by this class. If you want to manage the connection
    yourself, please just use ``__aenter__`` and ``__aexit__`` manually.

    Examples:

        Create a new connection (without connecting to the CAN bus)

        >>> connection = Connection()

    """

    def __init__(self) -> None:
        self.configuration = (
            settings.can.linux
            if platform == "linux"
            else (
                settings.can.mac
                if platform == "darwin"
                else settings.can.windows
            )
        )
        self.bus: BusABC | None = None
        self.notifier: Notifier | None = None

    async def __aenter__(self) -> STU:
        """Connect to the STU

        Returns:

            An object that can be used to communicate with the STU

        Raises:

            CANInitError: if the CAN initialization fails

        Examples:

            Import required library code

            >>> from asyncio import run

            Use a context manager to handle the cleanup process automatically

            >>> async def connect_can_context():
            ...     async with Connection() as stu:
            ...         pass
            >>> run(connect_can_context())

            Create and shutdown the connection explicitly

            >>> async def connect_can_manual():
            ...     connection = Connection()
            ...     connected = await connection.__aenter__()
            ...     await connection.__aexit__(None, None, None)
            >>> run(connect_can_manual())

        """

        def init():
            try:
                self.bus = Bus(  # pylint: disable=abstract-class-instantiated
                    channel=self.configuration.get("channel"),
                    interface=self.configuration.get("interface"),
                    bitrate=self.configuration.get("bitrate"),
                )  # type: ignore[abstract]
            except (PcanError, OSError) as error:
                raise CANInitError(
                    f"Unable to initialize CAN connection: {error}\n\n"
                    "Possible reasons:\n\n"
                    "• CAN adapter is not connected to the computer\n"
                    "• CAN adapter is in use by other program"
                ) from error

            self.bus.__enter__()

        await to_thread(init)

        assert isinstance(self.bus, BusABC)

        # We must set the event loop explicitly, otherwise the code will use
        # the synchronous API of python-can.
        self.notifier = Notifier(
            self.bus, listeners=[Logger()], loop=get_running_loop()
        )

        return STU(SPU(self.bus, self.notifier))

    async def __aexit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Disconnect CAN connection and clean up resources

        Args:

            exception_type:
                The type of the exception in case of an exception

            exception_value:
                The value of the exception in case of an exception

            traceback:
                The traceback in case of an exception

        """

        notifier = self.notifier
        if notifier is not None:
            await to_thread(notifier.stop)

        bus = self.bus
        if bus is not None:
            await to_thread(bus.shutdown)


# -- Main ---------------------------------------------------------------------

if __name__ == "__main__":
    from doctest import testmod

    testmod()
