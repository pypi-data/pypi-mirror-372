"""CAN error handling support"""

# -- Classes ------------------------------------------------------------------


class UnsupportedFeatureException(Exception):
    """Indicate that a certain feature is not supported by a node"""


class CANConnectionError(Exception):
    """Exception for errors regarding the ICOtronic CAN connection"""


class CANInitError(CANConnectionError):
    """Exception for CAN initialization problems"""


class ErrorResponseError(CANConnectionError):
    """Exception for erroneous response messages"""


class NoResponseError(CANConnectionError):
    """Thrown if no response message for a request was received"""
