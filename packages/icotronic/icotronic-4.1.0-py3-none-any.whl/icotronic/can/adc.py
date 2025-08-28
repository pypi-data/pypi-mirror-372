"""Support for ADC CAN commands and configuration

See:
https://mytoolit.github.io/Documentation/#command:Get-Set-ADC-Configuration

for more information
"""

# -- Imports ------------------------------------------------------------------

from collections.abc import Iterator, Mapping
from math import log2

from icotronic.utility.types import check_list

# -- Class --------------------------------------------------------------------


class ADCConfiguration(Mapping):
    """Support for reading and writing analog digital converter configuration

    Args:
        *data:
            A list containing the (first five) bytes of the ADC
            configuration

        set:
            Specifies if we want to set or retrieve (get) the ADC
            configuration

        prescaler:
            The ADC prescaler value (1 – 127); default: 2

        acquisition_time:
            The acquisition time in number of cycles
            (1, 2, 3, 4, 8, 16, 32, … , 256); default: 8

        oversampling_rate:
            The ADC oversampling rate (1, 2, 4, 8, … , 4096); default: 64

        reference_voltage:
            The ADC reference voltage in Volt
            (1.25, 1.65, 1.8, 2.1, 2.2, 2.5, 2.7, 3.3, 5, 6.6)

    Examples:

        Create simple ADC configuration from scratch

        >>> ADCConfiguration(prescaler=2,
        ...     acquisition_time=4,
        ...     oversampling_rate=64) # doctest:+NORMALIZE_WHITESPACE
        Get, Prescaler: 2, Acquisition Time: 4, Oversampling Rate: 64,
        Reference Voltage: 3.3 V

    """

    REFERENCE_VOLTAGES = [1.25, 1.65, 1.8, 2.1, 2.2, 2.5, 2.7, 3.3, 5, 6.6]

    # pylint: disable=too-many-branches

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *data: bytearray | list[int],
        # pylint: disable=redefined-builtin
        set: bool | None = None,
        # pylint: enable=redefined-builtin
        prescaler: int | None = None,
        acquisition_time: int | None = None,
        oversampling_rate: int | None = None,
        reference_voltage: float | None = None,
    ):
        if data:
            data_bytes = list(data[0])
            check_list(data_bytes, 5)
            self.data = data_bytes[0:5] + [0] * 3
        else:
            self.data = [0] * 8

        # ==================
        # = Get/Set Config =
        # ==================

        if set is not None:
            get_set_byte = self.data[0]
            # Set get/set to 0
            get_set_byte &= 0b01111111
            # Set value
            get_set_byte |= int(set) << 7
            self.data[0] = get_set_byte

        # =============
        # = Prescaler =
        # =============

        if prescaler is not None:
            self.prescaler = prescaler
        elif self.data[1] == 0:
            # Make sure default prescaler value makes sense
            self.prescaler = 2

        # ====================
        # = Acquisition Time =
        # ====================

        if acquisition_time is not None:
            self.acquisition_time = acquisition_time
        elif self.data[2] == 0:
            self.acquisition_time = 8

        # =====================
        # = Oversampling Rate =
        # =====================

        if oversampling_rate is not None:
            self.oversampling_rate = oversampling_rate
        elif self.data[3] == 0:
            self.oversampling_rate = 64

        # =====================
        # = Reference Voltage =
        # =====================

        if reference_voltage is not None:
            self.reference_voltage = reference_voltage
        elif self.data[4] == 0:
            # Make sure default reference voltage value makes sense
            self.reference_voltage = 3.3

        self.attributes = {
            "reference_voltage": self.reference_voltage,
            "prescaler": self.prescaler,
            "acquisition_time": self.acquisition_time,
            "oversampling_rate": self.oversampling_rate,
        }

    # pylint: enable=too-many-branches

    def __getitem__(self, item: str) -> float:
        """Return values of the mapping provided by this class

        Note:
            This method allow access to the object via the splat operators
            (*, **)

        Args:

            item:
                The attribute for which we want to retrieve the value

        Returns:

            The value of the attribute

        Examples:

            Convert ADC configurations into dictionary

            >>> dict(**ADCConfiguration()) # doctest:+NORMALIZE_WHITESPACE
            {'reference_voltage': 3.3,
             'prescaler': 2,
             'acquisition_time': 8,
             'oversampling_rate': 64}

            >>> dict(**ADCConfiguration(oversampling_rate=64)
            ...     ) # doctest:+NORMALIZE_WHITESPACE
            {'reference_voltage': 3.3,
             'prescaler': 2,
             'acquisition_time': 8,
             'oversampling_rate': 64}

        """

        return self.attributes[item]

    def __iter__(self) -> Iterator:
        """Return an iterator over the mapping provided by this class

        Note:

            This method allow access to the object via the splat operators
            (*, **)

        Returns:

            The names of the “important” properties of the ADC configuration:

            - reference voltage
            - prescaler
            - acquisition time
            - oversampling rate

        Examples:

            Print ADC attribute keys

            >>> for attribute in ADCConfiguration():
            ...     print(attribute)
            reference_voltage
            prescaler
            acquisition_time
            oversampling_rate

        """

        return iter(self.attributes)

    def __len__(self) -> int:
        """Return the length of the mapping provided by this class

        Note:

            This method allow access to the object via the splat operators
            (*, **)

        Returns:

            The amount of the “important” properties of the ADC configuration:

            - reference voltage
            - prescaler
            - acquisition time
            - oversampling rate

        Examples:

            Get the (constant) length of the ADC configuration

            >>> len(ADCConfiguration())
            4

            >>> len(ADCConfiguration(reference_voltage=3.3))
            4

        """

        return len(self.attributes)

    def __repr__(self) -> str:
        """Retrieve the textual representation of the ADC configuration

        Returns:

            A string that describes the ADC configuration

        Examples:

            Retrieve the string representation of ADC configurations

            >>> ADCConfiguration(prescaler=1, reference_voltage=3.3
            ... ) # doctest:+NORMALIZE_WHITESPACE
            Get, Prescaler: 1, Acquisition Time: 8, Oversampling Rate: 64,
            Reference Voltage: 3.3 V

            >>> ADCConfiguration(
            ...     set=True,
            ...     prescaler=64,
            ...     acquisition_time=128,
            ...     oversampling_rate=1024,
            ...     reference_voltage=1.8) # doctest:+NORMALIZE_WHITESPACE
            Set, Prescaler: 64, Acquisition Time: 128, Oversampling Rate: 1024,
            Reference Voltage: 1.8 V

            >>> ADCConfiguration(
            ...     [0, 2, 4, 6, 25]) # doctest:+NORMALIZE_WHITESPACE
            Get, Prescaler: 2, Acquisition Time: 8, Oversampling Rate: 64,
            Reference Voltage: 1.25 V

        """

        set_values = bool(self.data[0] >> 7)
        return ", ".join(["Set" if set_values else "Get", str(self)])

    def __str__(self) -> str:
        """Retrieve the informal representation of the ADC configuration

        Returns:
            A textual representation of the configuration

        Examples:

            Retrieve the textual representation of ADC configurations

            >>> print(ADCConfiguration(prescaler=1, reference_voltage=3.3
            ... )) # doctest:+NORMALIZE_WHITESPACE
            Prescaler: 1, Acquisition Time: 8, Oversampling Rate: 64,
            Reference Voltage: 3.3 V

            >>> print(ADCConfiguration(
            ...     set=True,
            ...     prescaler=64,
            ...     acquisition_time=128,
            ...     oversampling_rate=1024,
            ...     reference_voltage=1.8)) # doctest:+NORMALIZE_WHITESPACE
            Prescaler: 64, Acquisition Time: 128, Oversampling Rate: 1024,
            Reference Voltage: 1.8 V

            >>> print(ADCConfiguration(
            ...     [0, 2, 4, 6, 25])) # doctest:+NORMALIZE_WHITESPACE
            Prescaler: 2, Acquisition Time: 8, Oversampling Rate: 64,
            Reference Voltage: 1.25 V

        """

        parts = [
            f"Prescaler: {self.prescaler}",
            f"Acquisition Time: {self.acquisition_time}",
            f"Oversampling Rate: {self.oversampling_rate}",
            f"Reference Voltage: {self.reference_voltage} V",
        ]

        return ", ".join(parts)

    @property
    def reference_voltage(self) -> float:
        """Get the reference voltage

        Returns:

            The reference voltage in Volt

        Examples:

            Set and get different reference voltage values

            >>> config = ADCConfiguration(reference_voltage=3.3)
            >>> config.reference_voltage
            3.3
            >>> config.reference_voltage = 6.6
            >>> config.reference_voltage
            6.6

            >>> config = ADCConfiguration(reference_voltage=6.6)
            >>> config.reference_voltage
            6.6
            >>> config.reference_voltage = 1.8
            >>> config.reference_voltage
            1.8

            >>> config = ADCConfiguration(reference_voltage=1.8)
            >>> config.reference_voltage
            1.8

            Trying to set a unsupported reference voltage will fail

            >>> config.reference_voltage = 0 # doctest:+ELLIPSIS
            Traceback (most recent call last):
               ...
            ValueError: Reference voltage of “0” V out of range, please use ...

        """

        return self.data[4] / 20

    @reference_voltage.setter
    def reference_voltage(self, reference_voltage: float) -> None:
        """Change the reference voltage

        Args:

            reference_voltage:
                The new value for the reference voltage in V

        """

        cls = type(self)
        if reference_voltage not in cls.REFERENCE_VOLTAGES:
            raise ValueError(
                f"Reference voltage of “{reference_voltage}” V out of range"
                ", please use one of the following values: "
                + ", ".join(map(str, cls.REFERENCE_VOLTAGES))
            )

        self.data[4] = int(reference_voltage * 20)

    @property
    def prescaler(self) -> int:
        """Get the prescaler value

        Returns:

            The prescaler value

        Examples:

            Get initialised prescaler

            >>> config = ADCConfiguration(prescaler=127)
            >>> config.prescaler
            127

            Get prescaler set via property

            >>> config.prescaler = 20
            >>> config.prescaler
            20

            Trying to set an unsupported prescaler will fail

            >>> config.prescaler = 128 # doctest:+ELLIPSIS
            Traceback (most recent call last):
               ...
            ValueError: Prescaler value of “128” out of range, please use ...

        """

        return self.data[1]

    @prescaler.setter
    def prescaler(self, prescaler: int) -> None:
        """Change the prescaler value

        Args:

            prescaler:
                The new value for the prescaler

        """

        if not 1 <= prescaler <= 127:
            raise ValueError(
                f"Prescaler value of “{prescaler}” out of range"
                ", please use a value between 1 and 127"
            )
        self.data[1] = prescaler

    @property
    def acquisition_time(self) -> int:
        """Get the acquisition time

        Returns:

            The acquisition time

        Examples:

            Get initialised acquisition time

            >>> config = ADCConfiguration(acquisition_time=2)
            >>> config.acquisition_time
            2

            Get acquisition time set via property

            >>> config.acquisition_time = 128
            >>> config.acquisition_time
            128

            Trying to set an unsupported acquisition time will fail

            >>> config.acquisition_time = 5 # doctest:+ELLIPSIS
            Traceback (most recent call last):
               ...
            ValueError: Acquisition time of “5” out of range, please use ...

        """

        acquisition_time_byte = self.data[2]

        return (
            acquisition_time_byte + 1
            if acquisition_time_byte <= 3
            else 2 ** (acquisition_time_byte - 1)
        )

    @acquisition_time.setter
    def acquisition_time(self, acquisition_time: int) -> None:
        """Change the acquisition time value

        Args:

            acquisition_time:
                The new value for the acquisition time

        """

        possible_acquisition_times = list(range(1, 5)) + [
            2**value for value in range(3, 9)
        ]
        if acquisition_time not in possible_acquisition_times:
            raise ValueError(
                f"Acquisition time of “{acquisition_time}” out of range"
                ", please use one of the following values: "
                + ", ".join(map(str, possible_acquisition_times))
            )

        acquisition_time_byte = (
            acquisition_time - 1
            if acquisition_time <= 3
            else int(log2(acquisition_time)) + 1
        )

        self.data[2] = acquisition_time_byte

    @property
    def oversampling_rate(self) -> int:
        """Get the oversampling rate

        Returns:

            The oversampling rate

        Examples:

            Get initialised oversampling rate

            >>> config = ADCConfiguration(oversampling_rate=128)
            >>> config.oversampling_rate
            128

            Get oversampling rate set via property

            >>> config.oversampling_rate = 512
            >>> config.oversampling_rate
            512

            Trying to set an unsupported oversampling rate will fail

            >>> config.oversampling_rate = 3 # doctest:+ELLIPSIS
            Traceback (most recent call last):
               ...
            ValueError: Oversampling rate of “3” out of range, please use ...

        """

        oversampling_rate_byte = self.data[3]

        return 2**oversampling_rate_byte

    @oversampling_rate.setter
    def oversampling_rate(self, oversampling_rate: int) -> None:
        """Change the oversampling rate

        Args:

            oversampling_rate:
                The new value for the oversampling rate

        """

        possible_oversampling_rates = [2**value for value in range(13)]
        if oversampling_rate not in possible_oversampling_rates:
            raise ValueError(
                f"Oversampling rate of “{oversampling_rate}” out of "
                "range, please use one of the following values: "
                + ", ".join(map(str, possible_oversampling_rates))
            )

        self.data[3] = int(log2(oversampling_rate))

    def sample_rate(self) -> float:
        """Calculate the sampling rate for the current ADC configuration

        Returns:

            The calculated sample rate

        Examples:

            Get sampling rates based on ADC attribute values

            >>> round(ADCConfiguration(prescaler=2, acquisition_time=8,
            ...                        oversampling_rate=64).sample_rate())
            9524

            >>> round(ADCConfiguration(prescaler=8, acquisition_time=8,
            ...                        oversampling_rate=64).sample_rate())
            3175

            >>> round(ADCConfiguration(reference_voltage=5.0,
            ...                        prescaler=16,
            ...                        acquisition_time=8,
            ...                        oversampling_rate=128).sample_rate())
            840

        """

        clock_frequency = 38_400_000

        return clock_frequency / (
            (self.prescaler + 1)
            * (self.acquisition_time + 13)
            * self.oversampling_rate
        )


# -- Main ---------------------------------------------------------------------

if __name__ == "__main__":
    from doctest import testmod

    testmod()
