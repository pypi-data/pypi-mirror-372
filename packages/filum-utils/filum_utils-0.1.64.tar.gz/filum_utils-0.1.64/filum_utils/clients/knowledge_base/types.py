from typing import Any, Dict, List, Optional, TypedDict

from filum_utils.clients.knowledge_base.enums import (
    KBDocumentColumnDataTypeEnum,
    KBDocumentColumnFilterTypeEnum,
    KBDocumentStatusEnum,
)


class UpsertDocumentChunkDataType(TypedDict):
    text: str
    categories: List[str]
    summary: str


class UpsertDocumentColumnSchemaDataType(TypedDict, total=False):
    column_name: str
    data_type: KBDocumentColumnDataTypeEnum
    filter_type: Optional[KBDocumentColumnFilterTypeEnum]
    is_primary_key: bool


class UpsertDocumentDataType(TypedDict, total=False):
    document_id: str
    status: KBDocumentStatusEnum
    table_records: List[Dict[str, Any]]
    column_schemas: List[UpsertDocumentColumnSchemaDataType]
    collection_name: str


class PreprocessUpsertDocumentRequestType(TypedDict, total=False):
    document_id: str
    object_key: str
    status: KBDocumentStatusEnum
    sheet_name: Optional[str]
