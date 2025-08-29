from .base import BaseMessaging
from ..message_client.base import BaseClient

class Messaging(BaseMessaging):

    def __init__(self, client: BaseClient):
        self.client = client

    def send_message(self):
        return self.client.send()
