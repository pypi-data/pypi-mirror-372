from abc import ABC
from typing import Dict

from ...base import MessageType


class DirectMessage(MessageType, ABC):
    """
    Abstract base for direct messages.
    """

    messaging_type = "direct"

    def __init__(self, project: str, event: str, params: Dict, recipient: str):
        """

        :param project:
        :param event:
        :param params:
        :param recipient:
        """
        self.project = project
        self.event = event
        self.params = params
        self.recipient = recipient