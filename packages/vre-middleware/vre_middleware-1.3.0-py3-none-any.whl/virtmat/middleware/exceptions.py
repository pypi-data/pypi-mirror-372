"""specific exceptions for the vre-middleware"""


class CustomException(Exception):
    """Custom exception class used for all specific exceptions"""


class ConfigurationException(CustomException):
    """Describes errors in the configuration of the function or missing parameters"""


class InvalidStateException(CustomException):
    """Describes errors while being in a wrong state"""
    def __init__(self, msg, node_id):
        super().__init__(f'Node ID: {str(node_id)}: {msg}')


class TestingException(CustomException):
    """Describes an exception while running a test"""
    __test__ = False  # this is to prevent pytest collecting the class


class SlurmError(RuntimeError):
    """Exception to raise if Slurm is not responding or not available"""


class ResourceConfigurationError(CustomException):
    """Exception to raise from the resconfig module"""
