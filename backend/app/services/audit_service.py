from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.audit import AuditEvent

class AuditService:
    @staticmethod
    async def log_event(
        db: AsyncSession,
        organization_id: str,
        actor_type: str,
        action: str,
        entity_type: str,
        entity_id: str,
        actor_id: Optional[str] = None,
        actor_name: Optional[str] = None,
        old_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditEvent:
        """Create and commit an immutable audit event."""
        event = AuditEvent(
            organization_id=organization_id,
            actor_type=actor_type,
            actor_id=actor_id,
            actor_name=actor_name,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_state_json=old_state,
            new_state_json=new_state,
            ip_address=ip_address
        )
        db.add(event)
        await db.flush()
        return event

    @staticmethod
    async def get_org_audit_logs(
        db: AsyncSession,
        organization_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[AuditEvent]:
        """Fetch audit events for an organization in reverse chronological order."""
        stmt = (
            select(AuditEvent)
            .where(AuditEvent.organization_id == organization_id)
            .order_by(desc(AuditEvent.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_ticket_audit_logs(
        db: AsyncSession,
        organization_id: str,
        ticket_id: str,
        limit: int = 50
    ) -> List[AuditEvent]:
        """Fetch audit events associated with a specific ticket."""
        stmt = (
            select(AuditEvent)
            .where(
                AuditEvent.organization_id == organization_id,
                AuditEvent.entity_type == "ticket",
                AuditEvent.entity_id == ticket_id
            )
            .order_by(desc(AuditEvent.created_at))
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

