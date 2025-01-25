class APIError(Exception):
    """
    Standardized error response for API actions.
    """

    def __init__(self, message: str, status_code: int = None, details: dict = None):
        """
        :param message: An error message.
        :param data: The data related to the error.
        :param details: The dictionary for additional details related to error.
        """

        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

    def __str__(self):
        """
        Represantion of objects of the class.
        """
        return f"APIError: {self.message} (Status Code: {self.status_code})" if self.status_code else f"APIError: {self.message}"
