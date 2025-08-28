"""Code for measuring performance"""

# -- Imports ------------------------------------------------------------------

from time import perf_counter_ns, process_time_ns

# -- Classes ------------------------------------------------------------------


class PerformanceMeasurement:
    """Store information about performance measurements

    Examples:

        Import required library code

        >>> from time import sleep

        Determine performance data for sleep call

        >>> perf_measurement = PerformanceMeasurement()
        >>> perf_measurement.start()
        >>> sleep(0.5)
        >>> perf_measurement.stop()

        >>> 0.5 <= perf_measurement.run_time() < 0.7 * 10**9
        True
        >>> 0 <= perf_measurement.cpu_time() < 0.7 * 10**9
        True
        >>> perf_measurement.cpu_time() <= perf_measurement.run_time()
        True
        >>> 0 <= perf_measurement.cpu_usage() <= 1
        True

    """

    def __init__(self) -> None:
        self.perf_counter_start = 0
        self.process_time_start = 0

        self.perf_counter_end = 0
        self.process_time_end = 0

    def start(self) -> None:
        """Start performance measurement"""

        self.perf_counter_start = perf_counter_ns()
        self.process_time_start = process_time_ns()

        self.perf_counter_end = self.perf_counter_start
        self.process_time_end = self.process_time_start

    def stop(self) -> None:
        """Stop performance measurement"""
        self.perf_counter_end = perf_counter_ns()
        self.process_time_end = process_time_ns()

    def run_time(self) -> int:
        """Determine run time

        Returns:

            The amount of ns that the measured code executed in wall time

        """
        return self.perf_counter_end - self.perf_counter_start

    def cpu_time(self) -> int:
        """Determine CPU time

        Returns:

            The amount of ns that the measured code executed in the CPU

        """

        return self.process_time_end - self.process_time_start

    def cpu_usage(self) -> float:
        """Determine the CPU usage

        Returns:
            The CPU usage as factor between 0 and 1

        """

        return self.cpu_time() / self.run_time()

    def __repr__(self) -> str:
        """Print the textual representation of a performance measurement

        Returns:

            Textual data about performance measurement

        Examples:

            Import required library code

            >>> from time import sleep

            Print performance measurement data

            >>> perf_measurement = PerformanceMeasurement()
            >>> perf_measurement.start()
            >>> sleep(1)
            >>> perf_measurement.stop()
            >>> print(perf_measurement
            ...      ) # doctest:+ELLIPSIS, +NORMALIZE_WHITESPACE
            🏁 Run Time: ... seconds, 💼 CPU time: ... seconds,
            💪 CPU Usage: ... %

        """

        return ", ".join([
            f"🏁 Run Time: {self.run_time() / 10**9:.2f} seconds",
            f"💼 CPU time: {self.cpu_time() / 10**9:.2f} seconds",
            f"💪 CPU Usage: {self.cpu_usage() * 100:.2f} %",
        ])


# -- Main ---------------------------------------------------------------------

if __name__ == "__main__":
    from doctest import testmod

    testmod()
