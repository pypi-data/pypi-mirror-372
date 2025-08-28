from typing import List, Optional

from tenacity import retry

from filum_utils.clients.contact_center.common import _RETRY_PARAMS, ContactCenterClient
from filum_utils.clients.contact_center.types import (
    KBDocumentType,
    UpdateDocumentEmbeddingType,
)


class DocumentClient(ContactCenterClient):
    @retry(**_RETRY_PARAMS)
    def get_kb_document(self, organization_id: str, document_id: str) -> KBDocumentType:
        return self._request(
            endpoint=f"/internal/documents/{document_id}",
            method="GET",
            params={"organizationId": organization_id},
        )

    @retry(**_RETRY_PARAMS)
    def update_document_embedding_batch(
        self,
        organization_id: str,
        document_embeddings: List[UpdateDocumentEmbeddingType],
        batch_id: Optional[str] = None,
        batch_status: Optional[str] = None,
    ):
        request_body = {"batch_progress": 100, "documents": document_embeddings}
        if batch_id:
            request_body["batch_id"] = batch_id

        if batch_status:
            request_body["batch_status"] = batch_status

        self._request(
            endpoint="/internal/documents/embedding",
            method="PUT",
            params={"organizationId": organization_id},
            data=request_body,
        )
