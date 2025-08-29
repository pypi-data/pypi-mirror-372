from ..base import DirectMessage

from typing import Dict

class WhatsAppDirect(DirectMessage):
    """Concrete WhatsApp direct message."""

    def __init__(self, project: str, event: str, recipient: str, params: Dict):
        """

        :param project:
        :param event:
        :param recipient:
        :param params:
        """
        super().__init__(
            project=project,
            event=event,
            recipient=recipient,
            params=params
        )

    def build_payload(self) -> dict:
        return {
            "project": self.project,
            "event": self.event,
            "recipient": self.recipient,
            "params": self.params
        }