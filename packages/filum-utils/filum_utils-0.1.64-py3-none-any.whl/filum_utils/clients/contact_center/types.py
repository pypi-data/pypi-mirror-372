from typing import Any, Dict, List, Optional, TypedDict, Union

from filum_utils.clients.contact_center.enums import (
    ContactCenterMessageTypeEnum,
    DocumentColumnDataTypeEnum,
    DocumentColumnFilterTypeEnum,
    DocumentDataFormatEnum,
    DocumentSyncStatusEnum,
    MessageSenderTypeEnum,
    MessageStatusEnum,
    PubSubMessageEventNameEnum,
)


# Conversation Types
class MessageUserType(TypedDict, total=False):
    id: str
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    avatar: Optional[str]


class MessageAgentType(TypedDict, total=False):
    id: str
    name: Optional[str]
    email: Optional[str]


class MessageRecordingType(TypedDict, total=False):
    url: Optional[str]
    duration_seconds: Optional[int]


class MessageAttachmentType(TypedDict, total=False):
    internal_url: Optional[str]
    url: str
    size_bytes: Optional[int]
    sizeBytes: Optional[int]
    type: str
    name: Optional[str]
    mime_type: Optional[str]
    mimeType: Optional[str]
    is_sticker: Optional[bool]


class PubsubMessageEventType(TypedDict, total=False):
    original_conversation_id: Optional[str]
    conversation_name: Optional[str]
    timestamp: Optional[str]
    user: MessageUserType
    original_message_id: str
    sender_type: MessageSenderTypeEnum
    original_agent: Optional[MessageAgentType]
    call_center_phone: Optional[str]
    text: Optional[str]
    conversation_link: Optional[str]
    recording: Optional[MessageRecordingType]
    note: Optional[str]
    hangup_cause: Optional[str]
    charge_fee: Optional[float]
    attachments: Optional[List[MessageAttachmentType]]
    campaign_id: Optional[str]
    campaign_name: Optional[str]
    sync_outbound: Optional[bool]
    reply_to_original_message_id: Optional[str]
    is_test: Optional[bool]

    post_data: Optional[Dict[str, Any]]
    scope: Optional[str]
    type: Optional[ContactCenterMessageTypeEnum]
    is_hidden_in_third_party: Optional[bool]
    is_edited: Optional[bool]


class PubsubMessageStatusEventType(TypedDict, total=False):
    timestamp: Optional[str]
    original_message_id: str
    status: MessageStatusEnum
    internal_message_id: Optional[str]


class PubsubMessageType(TypedDict, total=False):
    access_token: str
    organization_id: str
    installed_source_id: int
    source_id: str
    source: str
    event_name: PubSubMessageEventNameEnum
    data: Union[PubsubMessageEventType, PubsubMessageStatusEventType]


# Document Types
class KnowledgeBaseType(TypedDict):
    id: str
    indexName: str


class KBDocumentType(TypedDict):
    knowledgeBase: KnowledgeBaseType
    _id: str
    name: str
    status: str
    embeddingStatus: str
    accountId: int
    organizationId: str
    createdAt: str
    updatedAt: str
    installedSourceId: int
    collectionName: Optional[str]


class ColumnSchemaType(TypedDict, total=False):
    column_name: str
    data_type: DocumentColumnDataTypeEnum
    filter_type: DocumentColumnFilterTypeEnum
    unique_count: int
    unique_values: List[str]
    array_value_delimiter: Optional[str]
    is_primary_key: bool


class UpdateDocumentEmbeddingType(TypedDict, total=False):
    document_id: str
    name: str
    description: Optional[str]
    status: DocumentSyncStatusEnum
    progress: int
    error_message: Optional[str]
    data_format: DocumentDataFormatEnum
    categories: List[str]
    collection_name: str
    column_schemas: List[ColumnSchemaType]
    table_records: List[Dict[str, Any]]
    objectKey: Optional[str]
