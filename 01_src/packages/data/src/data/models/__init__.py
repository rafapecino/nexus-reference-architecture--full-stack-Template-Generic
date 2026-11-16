from data.database import BaseXchg
from . import secondary as _secondary  # noqa: F401 — registra modelos en BaseXchg.metadata
from .audit_conversation import Conversation, ConversationMessage, LlmRun
from .audit_event import AuditEvent
from .item import Item
from .mixins import (
    AuditLogMixin,
    BlobReferenceMixin,
    DirtyFieldsMixin,
    FileAssetMixin,
    GeoMixin,
    OptimisticLockMixin,
    SoftDeleteMixin,
    StatusWorkflowMixin,
    TenantScopeMixin,
    TimestampMixin,
    UserAuditMixin,
    UUIDMixin,
    VersionedEntityMixin,
)
from .process_instance import ProcessInstance, ProcessStatus

__all__ = [
    # Core
    "BaseXchg",
    "AuditEvent",
    "Conversation", "ConversationMessage", "LlmRun",
    "Item",
    "ProcessInstance", "ProcessStatus",
    # Mixins
    "AuditLogMixin", "BlobReferenceMixin", "DirtyFieldsMixin", "FileAssetMixin",
    "GeoMixin", "OptimisticLockMixin", "SoftDeleteMixin", "StatusWorkflowMixin",
    "TenantScopeMixin", "TimestampMixin", "UserAuditMixin", "UUIDMixin", "VersionedEntityMixin",
]
