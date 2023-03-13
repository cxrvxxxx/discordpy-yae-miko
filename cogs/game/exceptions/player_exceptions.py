"""
This file containst all exceptions related to Players
"""

class PlayerNotFoundException(Exception):
    def __init__(self, message: str = "") -> None:
        self.message = message
        super().__init__(self.message)

class PlayerCreateException(Exception):
    def __init__(self, message: str = "") -> None:
        self.message = message
        super().__init__(self.message)
