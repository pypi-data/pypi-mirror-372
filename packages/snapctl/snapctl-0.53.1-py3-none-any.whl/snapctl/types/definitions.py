"""
This file contains the definitions of the types used in the snapctl package.
"""
from typing import List, Union


class ErrorResponse:
    """
    This class represents the response type of the Snapser API.
    """

    def __init__(self, error: bool, code: int, msg: str, data: Union[List, str]):
        self.error = error
        self.code = code
        self.msg = msg
        self.data = data

    def to_dict(self):
        '''
        Convert the object to a dictionary

        '''
        return {
            'error': self.error,
            'code': self.code,
            'msg': self.msg,
            'data': self.data
        }
