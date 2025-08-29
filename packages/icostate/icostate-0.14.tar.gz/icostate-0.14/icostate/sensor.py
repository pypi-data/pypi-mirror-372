"""Support code for sensor nodes"""

# -- Imports ------------------------------------------------------------------

from netaddr import EUI

from icotronic.can.adc import ADCConfiguration

# -- Classes ------------------------------------------------------------------

# pylint: disable=too-few-public-methods


class SensorNodeAttributes:
    """Store information about a sensor node

    Args:

        name:

            The Bluetooth advertisement name of the sensor node

        mac_address:

            The MAC address of the sensor node

        adc_configuration:

            The ADC configuration of the sensor node

    """

    def __init__(
        self,
        name: str,
        mac_address: EUI,
        adc_configuration: ADCConfiguration,
    ) -> None:
        self.name: str = name
        self.mac_address: EUI = mac_address
        self.adc_configuration: ADCConfiguration = adc_configuration

    def __repr__(self) -> str:
        """Get the textual representation of the sensor node

        Returns:

            A string containing information about the sensor node attributes

        Examples:

            Get representation sensor node with all attributes defined


            >>> config = ADCConfiguration(prescaler=2,
            ...                           acquisition_time=8,
            ...                           oversampling_rate=64)
            >>> SensorNodeAttributes(name="hello",
            ...                      mac_address=EUI("12-34-56-78-90-AB"),
            ...                      adc_configuration=config
            ...                     ) # doctest:+NORMALIZE_WHITESPACE
                Name: hello
                MAC Address: 12-34-56-78-90-AB
                ADC:
                  Prescaler: 2
                  Acquisition Time: 8
                  Oversampling Rate: 64
                  Reference Voltage: 3.3 V

        """

        adc = str(self.adc_configuration).replace(", ", "\n  ")
        return "\n".join([
            f"Name: {self.name}",
            f"MAC Address: {self.mac_address}",
            f"ADC:\n  {adc}",
        ])


# pylint: enable=too-few-public-methods

# -- Main ---------------------------------------------------------------------

if __name__ == "__main__":
    from doctest import testmod

    testmod()
