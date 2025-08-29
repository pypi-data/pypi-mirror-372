import os


class BaseDomain:

    DOMAIN_URL = os.getenv("BASE_URL", "")

    BASE_URL = f"{DOMAIN_URL}/api/v1/messaging/"
