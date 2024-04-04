class DwfException(Exception):
    def __init__(self, code: int = -1, error: str = "", message: str = ""):
        super().__init__(message)
        self.code = code
        self.error = error
        self.message = message
