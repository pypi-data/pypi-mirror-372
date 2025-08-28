"""Listeners used to react to different messages from the CAN bus"""

# -- Imports ------------------------------------------------------------------

from __future__ import annotations

from asyncio import Queue
from collections.abc import Sequence
from logging import getLogger
from typing import NamedTuple

from can import Listener, Message as CANMessage

from icotronic.can.protocol.message import Message
from icotronic.config import settings
from icotronic.utility.log import get_log_file_handler

# -- Classes ------------------------------------------------------------------


class Response(NamedTuple):
    """Used to store a response (message)"""

    message: CANMessage
    """The response message"""

    is_error: bool
    """States if the response was an error or a normal response"""

    error_message: str
    """Optional explanation for the error reason"""


class Logger(Listener):
    """Log ICOtronic CAN messages in a machine and human readable format"""

    def __init__(self):
        self.logger = getLogger("icotronic.can")
        self.logger.propagate = False
        # We use `Logger` in the code below, since the `.logger` attribute
        # stores internal DynaConf data
        self.logger.setLevel(settings.Logger.can.level)
        self.logger.addHandler(get_log_file_handler("can.log"))

    def on_message_received(self, msg: CANMessage) -> None:
        """React to a received message on the bus

        Args:

            msg:
                The received CAN message the notifier should react to

        """

        self.logger.debug("%s", Message(msg))

    def on_error(self, exc: Exception) -> None:
        """Handle any exception in the receive thread.

        Args:

            exc:
                The exception causing the thread to stop

        """

        self.logger.error("Error while monitoring CAN bus data: %s", exc)

    def stop(self) -> None:
        """Stop handling new messages"""


class ResponseListener(Listener):
    """A listener that reacts to messages containing a certain id

    Args:

        message:
            The sent message this listener should react to

        expected_data:
           This optional field specifies the expected acknowledgment data.
           You can either specify to:

           - not check the message data (``None``),
           - check the first bytes by providing a bytearray,
           - check the first bytes by providing a heterogenous list
             of numbers (data byte will be checked for equality) and
             ``None`` (data byte will not be checked).
    """

    def __init__(
        self,
        message: Message,
        expected_data: bytearray | Sequence[int | None] | None,
    ) -> None:

        self.queue: Queue[Response] = Queue()
        identifier = message.identifier()
        self.acknowledgment_identifier = identifier.acknowledge()
        self.error_identifier = identifier.acknowledge(error=True)
        self.expected_data = expected_data

    def on_message_received(self, msg: CANMessage) -> None:
        """React to a received msg on the bus

        Args:

            msg:
                The received CAN message the notifier should react to

        """

        identifier = msg.arbitration_id
        error_response = identifier == self.error_identifier.value
        normal_response = identifier == self.acknowledgment_identifier.value

        # We only store CAN messages that contain the expected (error) response
        # message identifier

        # Also set an error response, if the retrieved message data does not
        # match the expected data
        expected_data = self.expected_data
        error_reason = ""
        if normal_response and expected_data is not None:
            error_response |= any(
                expected != data
                for expected, data in zip(expected_data, msg.data)
                if expected is not None
            )
            error_reason = (
                "Unexpected response message data:\n"
                f"Expected: {list(expected_data)}\n"
                f"Received: {list(msg.data)}"
            )
        elif error_response:
            error_reason = "Received error response"

        if error_response or normal_response:
            self.queue.put_nowait(
                Response(
                    message=msg,
                    is_error=error_response,
                    error_message=error_reason,
                )
            )

    async def on_message(self) -> Response | None:
        """Return answer messages for the specified message identifier

        Returns:

            A response containing

            - the response message for the message with the identifier given at
              object creation, and
            - the error status of the response message

        """

        return await self.queue.get()

    def on_error(self, exc: Exception) -> None:
        """Handle any exception in the receive thread

        Args:

            exc:
                The exception causing the thread to stop

        """

        getLogger().error("Error while monitoring CAN bus data: %s", exc)

    def stop(self) -> None:
        """Stop handling new messages"""


# -- Main ---------------------------------------------------------------------

if __name__ == "__main__":
    from doctest import testmod

    testmod()
