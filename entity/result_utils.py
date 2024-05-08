from typing import Optional


class ResultDo:
    def __init__(self, code: int, message: Optional[str], data: Optional[object]):
        self.code = code
        self.message = message
        self.data = data

    @property
    def code(self):
        return self.code

    @property
    def message(self):
        return self.message

    @property
    def data(self):
        return self.data
