from abc import ABC, abstractmethod


class MessageType(ABC):
    """
    Abstract base for all message types.
    """

    messaging_type: str

    @property
    def get_messaging_type(self):
        return self.messaging_type

    @abstractmethod
    def build_payload(self) -> dict:
        pass