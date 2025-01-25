class APISuccess:
    """
    Standardized success response for API actions.
    """

    def __init__(self, message: str, details: dict = None) -> None:
        """
        :param message: A success message.
        :param details: The details related to the successful action.
        """
        self.message = message
        self.details = details

    def to_dict(self) -> dict:
        """
        Converts the success response to a dictionary format.
        """
        return {
            "message": self.message,
            "details": self.details
        }
