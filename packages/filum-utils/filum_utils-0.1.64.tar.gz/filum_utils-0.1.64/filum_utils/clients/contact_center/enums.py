from enum import Enum


# Conversation Enums
class MessageSenderTypeEnum(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    AI = "ai"


class ContactCenterMessageTypeEnum(str, Enum):
    CHAT = "chat"
    COMMENT = "comment"


class MessageStatusEnum(str, Enum):
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
    SEEN = "seen"


class PubSubMessageEventNameEnum(str, Enum):
    MESSAGE_CREATED = "Message Created"
    MESSAGE_STATUS_UPDATED = "Message Status Updated"
    CALL_CREATED = "Call Created"


# Document Enums
class DocumentStatusEnums(str, Enum):
    DRAFT = "draft"
    PREPROCESSING = "preprocessing"
    PREPROCESSED = "preprocessed"
    EMBEDDING = "embedding"
    FAILED = "failed"
    INACTIVE = "inactive"
    ACTIVE = "active"
    DELETING = "deleting"
    DELETED = "deleted"


class DocumentSyncStatusEnum(str, Enum):
    PENDING = "pending"
    PREPROCESSING = "preprocessing"
    PROCESSING = "processing"
    EMBEDDING = "embedding"
    FAILED = "failed"
    SUCCESS = "success"


class DocumentDataFormatEnum(str, Enum):
    TABLE = "table"
    VECTOR = "vector"


class DocumentColumnDataTypeEnum(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    GEOLOCATION = "geolocation"
    IMAGE = "image"
    DATE = "date"
    ARRAY = "array"
    OBJECT = "object"


class DocumentColumnFilterTypeEnum(str, Enum):
    ENUM = "enum"
    RANGE = "range"
    TEXT = "text"
