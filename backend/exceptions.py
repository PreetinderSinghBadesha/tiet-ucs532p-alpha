"""
exceptions.py — Custom exceptions for DERMA.ai backend.
"""


class FaceNotDetectedError(Exception):
    """Raised when no face can be found in the supplied image."""
    pass


class InvalidImageError(Exception):
    """Raised when the image cannot be decoded or is malformed."""
    pass
