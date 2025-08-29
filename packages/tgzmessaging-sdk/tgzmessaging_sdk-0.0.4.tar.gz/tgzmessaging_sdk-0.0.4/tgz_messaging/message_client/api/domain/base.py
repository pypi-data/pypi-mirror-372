import os


class BaseDomain:

    BASE_DOMAIN_URL = os.getenv("BASE_DOMAIN_URL")

    BASE_URL = f"{BASE_DOMAIN_URL}/api/v1/api-gateway/messaging/"
