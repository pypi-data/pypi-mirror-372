from tenacity import (
    retry_if_exception,
    stop_after_attempt,
    stop_after_delay,
    wait_fixed,
)

from filum_utils.clients.common import BaseClient, retry_if_error
from filum_utils.config import config

_RETRY_PARAMS = {
    "reraise": True,
    "wait": wait_fixed(10),
    "stop": (stop_after_attempt(6) | stop_after_delay(60)),
    "retry": retry_if_exception(retry_if_error),
}


class ContactCenterClient(BaseClient):
    def __init__(self):
        super().__init__(
            base_url=config.CONVERSATION_BASE_URL,
            username=config.CONVERSATION_USERNAME,
            password=config.CONVERSATION_PASSWORD,
        )
