from typing import Any, Dict, List

from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    stop_after_delay,
    wait_fixed,
)

from filum_utils.clients.common import BaseClient, retry_if_error
from filum_utils.clients.knowledge_base.enums import KBDocumentStatusEnum
from filum_utils.clients.knowledge_base.types import (
    PreprocessUpsertDocumentRequestType,
    UpsertDocumentDataType,
)
from filum_utils.config import config

_RETRY_PARAMS = {
    "reraise": True,
    "wait": wait_fixed(10),
    "stop": (stop_after_attempt(6) | stop_after_delay(60)),
    "retry": retry_if_exception(retry_if_error),
}


class KnowledgeBaseClient(BaseClient):
    def __init__(self, organization_id: str):
        super().__init__(
            base_url=config.KNOWLEDGE_BASE_SERVICE_URL,
            username=config.KNOWLEDGE_BASE_SERVICE_USERNAME,
            password=config.KNOWLEDGE_BASE_SERVICE_PASSWORD,
        )
        self._organization_id = organization_id

    @retry(**_RETRY_PARAMS)
    def upsert_documents(
        self, documents: List[UpsertDocumentDataType]
    ) -> Dict[str, Any]:
        return self._request(
            method="PUT",
            endpoint="/documents/from-records",
            params={"organization_id": self._organization_id},
            data={"documents": documents},
        )

    @retry(**_RETRY_PARAMS)
    def delete_document(self, document_id: str):
        return self._request(
            method="DELETE",
            endpoint=f"/documents/{document_id}",
            params={"organization_id": self._organization_id},
        )

    @retry(**_RETRY_PARAMS)
    def update_document_status(
        self, document_id: str, new_status: KBDocumentStatusEnum
    ):
        return self._request(
            method="PUT",
            endpoint=f"/documents/{document_id}",
            params={"organization_id": self._organization_id},
            data={"status": new_status},
        )

    @retry(**_RETRY_PARAMS)
    def preprocess_upsert_document(
        self, documents: List[PreprocessUpsertDocumentRequestType]
    ):
        self._request(
            method="POST",
            endpoint="/documents/preprocess-upsert-jobs",
            params={"organization_id": self._organization_id},
            data={"documents": documents},
        )
