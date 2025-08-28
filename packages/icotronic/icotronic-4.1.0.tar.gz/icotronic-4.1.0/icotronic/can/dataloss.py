"""Support for calculating dataloss statistics of ICOtronic CAN messages"""

# -- Imports ------------------------------------------------------------------

from collections.abc import Iterable

# -- Classes ------------------------------------------------------------------


class MessageStats:
    """Store message statistics

    Args:

        retrieved:
            The number of successfully retrieved messages

    """

    def __init__(self, retrieved: int = 0, lost: int = 0):

        self.retrieved = retrieved
        """Number of retrieved messages/streaming data elements"""

        self.lost = lost
        """Number of lost messages/streaming data elements"""

    def __repr__(self):
        """Get the textual representation of the message statistics

        Returns:

            A string representing the message statistics

        Examples:

            Get string representation of example data

            >>> MessageStats(retrieved=950, lost=50)
            Retrieved: 950, Lost: 50, Dataloss: 0.05

        """

        return ", ".join([
            f"Retrieved: {self.retrieved}",
            f"Lost: {self.lost}",
            f"Dataloss: {self.dataloss()}",
        ])

    def dataloss(self) -> float:
        """Get the amount of data loss

        Returns:

            The overall amount of dataloss as number between 0 (no data loss)
            and 1 (all data lost).

        Examples:

            Get the dataloss for some example data

            >>> MessageStats().dataloss()
            0
            >>> MessageStats(50, 50).dataloss()
            0.5
            >>> MessageStats(retrieved=960, lost=40).dataloss()
            0.04
            >>> MessageStats(retrieved=490, lost=10).dataloss()
            0.02
            >>> MessageStats(retrieved=0, lost=0).dataloss()
            0

        """

        overall = self.retrieved + self.lost

        return 0 if overall == 0 else self.lost / overall

    def reset(self) -> None:
        """Reset the amount of retrieved and lost messages to 0

        Examples:

            Reset stats for some example data

            >>> stats = MessageStats(10, 90)
            >>> stats.dataloss()
            0.9
            >>> stats.reset()
            >>> stats.dataloss()
            0

        """

        self.retrieved = 0
        self.lost = 0


# -- Functions ----------------------------------------------------------------


def calculate_dataloss_stats(counters: Iterable[int]) -> MessageStats:
    """Determine number of lost and received messages based on message counters

    Returns:

        Tuple containing the number of received and the number of lost
        messages

    Examples:

        Get data loss statistics for example counters

        >>> counters = [counter for counter in range(256)]
        >>> counters.extend([counter for counter in range(128, 256)])
        >>> stats = calculate_dataloss_stats(counters)
        >>> stats.retrieved
        384
        >>> stats.lost
        128

        >>> counters = [1, 1, 1, 9, 9, 9, 10, 10, 10]
        >>> calculate_dataloss_stats(counters)
        Retrieved: 3, Lost: 7, Dataloss: 0.7

    """

    iterator = iter(counters)

    try:
        last_counter = next(iterator)
    except StopIteration:
        return MessageStats()

    assert last_counter is not None
    lost_messages = 0
    retrieved_messages = 1

    for counter in iterator:
        if counter == last_counter:
            continue  # Skip data with same message counter

        retrieved_messages += 1

        lost_messages += (counter - last_counter) % 256 - 1

        last_counter = counter

    return MessageStats(retrieved=retrieved_messages, lost=lost_messages)
