from abc import ABC, abstractmethod

from ..api import APIRequest
from ...message_type.base import MessageType

class BaseClient(ABC, APIRequest):
    """
    Abstract base client.
    """

    messaging_product: str
    payload: dict

    def __init__(self, message_type: MessageType):
        """

        :param message_type:
        """
        self.message_type = message_type

    @abstractmethod
    def send(self):
        pass