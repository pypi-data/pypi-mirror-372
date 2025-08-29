from ..base import BaseClient
from ...message_type.base import MessageType

class WhatsAppClient(BaseClient):
    """
    Concrete WhatsApp client.
    """

    messaging_product: str = "whatsapp"

    def __init__(self, message_type: MessageType):
        """

        :param message_type:
        """
        super().__init__(message_type)


    def send(self):
        """

        :return:
        """
        self.payload = self.message_type.build_payload()

        self.payload["messaging_product"] = self.messaging_product

        return self.send_api_request()
