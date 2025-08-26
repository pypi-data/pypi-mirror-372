class IgnoreScoreException(Exception):
    """
    Exception to indicate that a score should be ignored/is not applicable.
    Accepts a custom message explaining why the score was ignored.
    """

    def __init__(self, message: str = "Score should be ignored"):
        super().__init__(message)
        self.message = message
