from abc import ABC, abstractmethod

class BaseMessaging(ABC):
    """Abstract messaging facade."""

    @abstractmethod
    def send_message(self):
        pass