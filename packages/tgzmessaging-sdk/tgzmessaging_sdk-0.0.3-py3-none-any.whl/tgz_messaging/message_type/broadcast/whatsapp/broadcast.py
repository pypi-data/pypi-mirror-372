from typing import List, Dict

from ..base import BroadcastMessage

class WhatsAppBroadcast(BroadcastMessage):

    def __init__(self, project: str, event:str, recipients: List[str], params: Dict):
        """

        :param project:
        :param event:
        :param recipients:
        :param params:
        """
        super().__init__(
            project=project,
            event=event,
            recipients=recipients,
            params=params
        )

    def build_payload(self) -> dict:
        return {
            "project": self.project,
            "event": self.event,
            "recipients": self.recipients,
            "params": self.params
        }