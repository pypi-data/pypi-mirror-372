from typing import List, Optional

from tenacity import retry

from filum_utils.clients.contact_center.common import _RETRY_PARAMS, ContactCenterClient
from filum_utils.clients.contact_center.types import MessageAttachmentType


class ConversationClient(ContactCenterClient):
    @retry(**_RETRY_PARAMS)
    def update_origin_message_id(
        self,
        organization_id: str,
        conversation_id: str,
        message_id: str,
        original_message_id: Optional[str],
        status: Optional[str] = None,
        failed_reason: Optional[str] = None,
        failed_reason_type: Optional[str] = None,
        attachments: Optional[List[MessageAttachmentType]] = None,
    ):
        request_data = {}
        if original_message_id:
            request_data["messageId"] = original_message_id

        if status:
            request_data["status"] = status

        if failed_reason:
            request_data["failedReason"] = failed_reason

        if failed_reason_type:
            request_data["failedReasonType"] = failed_reason_type

        if attachments:
            request_data["attachments"] = attachments

        if not request_data:
            return

        self._request(
            method="PUT",
            endpoint=f"/internal/conversations/{conversation_id}/messages/{message_id}",
            data=request_data,
            params={
                "organizationId": organization_id,
            },
        )
