import requests

from .domain import BaseDomain

class APIRequest(BaseDomain):
    """
    Reusable request sender that builds the URL dynamically.
    """

    def send_api_request(self):

        url = f"{self.BASE_URL}{self.messaging_product}/{self.message_type.messaging_type}/"

        response = requests.post(
            url, json=self.payload
        )

        return {
            "status_code": response.status_code,
            "response": response.json() if response.content else {}
        }