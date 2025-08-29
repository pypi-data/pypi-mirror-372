"""Support code for determining the current state of the ICOtronic system"""

# -- Imports ------------------------------------------------------------------

from enum import Enum

# -- Classes ------------------------------------------------------------------


class State(str, Enum):
    """Contains the various states the ICOtronic system can be in

    Examples:

        Get state variables

        >>> State.DISCONNECTED
        <State.DISCONNECTED: 'DISCONNECTED'>

        >>> State.STU_CONNECTED
        <State.STU_CONNECTED: 'STU_CONNECTED'>

        >>> State.SENSOR_NODE_CONNECTED
        <State.SENSOR_NODE_CONNECTED: 'SENSOR_NODE_CONNECTED'>

    """

    DISCONNECTED = "DISCONNECTED"
    STU_CONNECTED = "STU_CONNECTED"
    SENSOR_NODE_CONNECTED = "SENSOR_NODE_CONNECTED"
    MEASUREMENT = "MEASUREMENT"

    def __str__(self) -> str:
        """Get informal string representation of state

        Returns:

            A human readable unique representation of the state

        Examples:

            Show the string representation of some states

            >>> print(State.STU_CONNECTED)
            STU Connected

            >>> print(State.DISCONNECTED)
            Disconnected

        """

        return " ".join([
            word.upper() if word in {"STH", "STU"} else word.capitalize()
            for word in self.name.split("_")
        ])


# -- Main ---------------------------------------------------------------------

if __name__ == "__main__":
    from doctest import testmod

    testmod()
