# This file is intentionally left blank. /ᐠ｡ꞈ｡ᐟ\ 喵~ not anymore !


class BaseResponse:
    """
    A base mock response class for simulating HTTP responses in tests.

    Attributes:
        status_code (int): The HTTP status code of the response. Defaults to 200.

    Methods:
        raise_for_status(): Simulates the behavior of `requests.Response.raise_for_status()`
            by doing nothing, indicating a successful response with no exceptions raised.
    """

    status_code = 200

    @staticmethod
    def raise_for_status():
        """Simulates a successful response with no exceptions raised."""
        pass
