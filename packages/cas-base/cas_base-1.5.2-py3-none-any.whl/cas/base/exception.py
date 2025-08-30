class FriendlyException(Exception):

    def __init__(self, message: str, code: int = 500, status_code: int = 200, desc: str = None):
        self.message = message
        self.code = code
        self.desc = desc
        self.status_code = status_code
