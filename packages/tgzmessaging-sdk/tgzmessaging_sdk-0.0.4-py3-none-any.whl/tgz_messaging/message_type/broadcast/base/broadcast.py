from abc import ABC
from typing import Dict, List

from ...base import MessageType


class BroadcastMessage(MessageType, ABC):
    """
    Abstract base for broadcast messages.
    """

    messaging_type = "broadcast"

    def __init__(self, project: str, event: str, recipients: List[str], params: Dict):
        """

        :param project:
        :param event:
        :param recipients:
        :param params:
        """
        self.project = project
        self.event = event
        self.params = params
        self.recipients = recipients