import os
import uuid
import random
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, desc
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status, UploadFile

from app.models.organization import User
from app.models.customer import Customer
from app.models.ticket import Ticket, TicketMessage, TicketAttachment, TicketClassification
from app.models.voice import VoiceTranscript, ExtractedEntity
from app.models.investigation import Investigation, InvestigationEvent
from app.models.business_mock import Order, Payment
from app.core.state_machine import TicketStateMachine, TicketStatus
from app.core.pii_masking import mask_pii_for_prompts
from app.schemas.ticket import (
    TicketCreate, TicketListResponse, TicketListItem,
    TicketDetailResponse, CustomerSummary, OrderSummary, PaymentSummary,
    ClassificationResponse, VoiceTranscriptResponse, ExtractedEntityResponse,
    InvestigationSummaryResponse, MessageResponse, AttachmentResponse
)
from app.services.audit_service import AuditService
from app.config import settings

class TicketService:
    @staticmethod
    async def generate_ticket_number(db: AsyncSession) -> str:
        """Generate unique human-readable ticket number (e.g. TCK-10482)."""
        for _ in range(10):
            candidate = f"TCK-{random.randint(10000, 99999)}"
            res = await db.execute(select(Ticket.id).where(Ticket.ticket_number == candidate))
            if not res.scalar_one_or_none():
                return candidate
        return f"TCK-{uuid.uuid4().hex[:6].upper()}"

    @staticmethod
    async def create_ticket(
        db: AsyncSession,
        organization_id: str,
        actor_id: Optional[str],
        actor_name: Optional[str],
        payload: TicketCreate,
        audio_file: Optional[UploadFile] = None
    ) -> Ticket:
        """Create a new ticket from manual input, support form, simulated email, or voice note."""
        now = datetime.now(timezone.utc)

        # 1. Customer Lookup or Creation
        cust_res = await db.execute(
            select(Customer).where(
                and_(
                    Customer.organization_id == organization_id,
                    Customer.email == payload.customer_email
                )
            )
        )
        customer = cust_res.scalar_one_or_none()
        if not customer:
            customer = Customer(
                organization_id=organization_id,
                external_id=f"CUST-{random.randint(1000, 9999)}",
                full_name=payload.customer_name,
                email=payload.customer_email,
                phone=payload.customer_phone,
                segment="standard",
                risk_score=0.1,
                metadata_json={"city": "Karachi", "source": payload.channel}
            )
            db.add(customer)
            await db.flush()

        # 2. PII / PCI Masking on user-supplied content
        clean_subject = mask_pii_for_prompts(payload.subject)
        clean_description = mask_pii_for_prompts(payload.description)

        ticket_number = await TicketService.generate_ticket_number(db)

        # Determine priority/urgency
        priority = payload.priority or "s3_medium"
        urgency = payload.urgency or "medium"
        sla_hours = 1 if priority == "s1_critical" else (4 if priority == "s2_high" else (12 if priority == "s3_medium" else 24))

        ticket = Ticket(
            organization_id=organization_id,
            ticket_number=ticket_number,
            customer_id=customer.id,
            channel=payload.channel,
            status=TicketStatus.NEW.value,
            priority=priority,
            urgency=urgency,
            sentiment="neutral",
            subject=clean_subject,
            description=clean_description,
            sla_due_at=now + timedelta(hours=sla_hours),
            created_at=now,
            updated_at=now
        )
        db.add(ticket)
        await db.flush()

        # 3. Create initial customer message
        first_msg = TicketMessage(
            ticket_id=ticket.id,
            sender_type="customer",
            sender_id=customer.id,
            content=clean_description,
            language="en",
            is_internal_note=False,
            created_at=now
        )
        db.add(first_msg)

        # 4. Create initial classification
        category = payload.category or "payment_pending"
        classification = TicketClassification(
            ticket_id=ticket.id,
            category=category,
            subcategory="intake_triage",
            severity="S1" if priority == "s1_critical" else ("S2" if priority == "s2_high" else "S3"),
            confidence=0.92,
            reasoning=f"Automatic classification based on channel '{payload.channel}' and category '{category}'.",
            fraud_risk_score=0.05,
            created_at=now
        )
        db.add(classification)

        # 5. Extract initial entities if provided
        if payload.order_number:
            db.add(ExtractedEntity(
                ticket_id=ticket.id,
                entity_type="order_id",
                entity_value=payload.order_number.strip(),
                confidence=0.99,
                is_masked=False,
                created_at=now
            ))
        if payload.transaction_id:
            db.add(ExtractedEntity(
                ticket_id=ticket.id,
                entity_type="transaction_id",
                entity_value=payload.transaction_id.strip(),
                confidence=0.99,
                is_masked=False,
                created_at=now
            ))

        # 6. Audio File Handling if present
        if audio_file:
            audio_ext = os.path.splitext(audio_file.filename or "voice.mp3")[1].lower().replace(".", "") or "mp3"
            filename = f"{ticket.id}_{uuid.uuid4().hex[:8]}.{audio_ext}"
            file_path = os.path.join(settings.STORAGE_DIR, "audio", filename)

            content = await audio_file.read()
            with open(file_path, "wb") as f:
                f.write(content)

            voice_transcript = VoiceTranscript(
                ticket_id=ticket.id,
                audio_storage_url=f"/storage/audio/{filename}",
                audio_format=audio_ext,
                duration_seconds=12.0,
                detected_language="en",
                transcript_raw=clean_description,
                transcript_edited=clean_description,
                segments_json=[{"start": 0.0, "end": 12.0, "text": clean_description}],
                confidence_score=0.95,
                is_edited=False,
                created_at=now
            )
            db.add(voice_transcript)

        # 7. Audit Event
        await AuditService.log_event(
            db=db,
            organization_id=organization_id,
            actor_type="user" if actor_id else "customer",
            actor_id=actor_id,
            actor_name=actor_name or customer.full_name,
            action="ticket.created",
            entity_type="ticket",
            entity_id=ticket.id,
            new_state={
                "ticket_number": ticket.ticket_number,
                "channel": ticket.channel,
                "status": ticket.status,
                "priority": ticket.priority
            }
        )

        await db.flush()
        return ticket

    @staticmethod
    async def list_tickets(
        db: AsyncSession,
        organization_id: str,
        status_filter: Optional[str] = None,
        channel: Optional[str] = None,
        severity: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        assignee: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 15,
        current_user_id: Optional[str] = None
    ) -> TicketListResponse:
        """Omnichannel inbox listing with status tabs aggregation, multi-filters, and search."""
        # 1. Aggregate status counts across organization for top navigation tabs
        counts_stmt = (
            select(Ticket.status, func.count(Ticket.id))
            .where(Ticket.organization_id == organization_id)
            .group_by(Ticket.status)
        )
        counts_res = await db.execute(counts_stmt)
        status_counts: Dict[str, int] = {
            "all": 0,
            "new": 0,
            "triaged": 0,
            "investigating": 0,
            "waiting_for_approval": 0,
            "waiting_for_customer": 0,
            "waiting_for_internal_team": 0,
            "resolved": 0,
            "closed": 0,
        }
        total_org_tickets = 0
        for s_key, s_cnt in counts_res.all():
            if s_key in status_counts:
                status_counts[s_key] = s_cnt
            total_org_tickets += s_cnt
        status_counts["all"] = total_org_tickets

        # 2. Build filtered query
        query = (
            select(
                Ticket,
                Customer,
                User,
                TicketClassification,
                VoiceTranscript.id.label("voice_id")
            )
            .join(Customer, Ticket.customer_id == Customer.id)
            .outerjoin(User, Ticket.assigned_user_id == User.id)
            .outerjoin(TicketClassification, Ticket.id == TicketClassification.ticket_id)
            .outerjoin(VoiceTranscript, Ticket.id == VoiceTranscript.ticket_id)
            .where(Ticket.organization_id == organization_id)
        )

        # Status filter
        if status_filter and status_filter.lower() != "all":
            query = query.where(Ticket.status == status_filter.lower())

        # Channel filter
        if channel and channel.lower() != "all":
            query = query.where(Ticket.channel == channel.lower())

        # Priority filter
        if priority and priority.lower() != "all":
            query = query.where(Ticket.priority == priority.lower())

        # Severity filter
        if severity and severity.lower() != "all":
            query = query.where(TicketClassification.severity == severity.upper())

        # Category filter
        if category and category.lower() != "all":
            query = query.where(TicketClassification.category == category.lower())

        # Assignee filter
        if assignee:
            if assignee.lower() == "unassigned":
                query = query.where(Ticket.assigned_user_id.is_(None))
            elif assignee.lower() == "me" and current_user_id:
                query = query.where(Ticket.assigned_user_id == current_user_id)
            elif assignee.lower() != "all":
                query = query.where(Ticket.assigned_user_id == assignee)

        # Search filter across ticket number, subject, description, customer name/email
        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.where(
                or_(
                    Ticket.ticket_number.ilike(term),
                    Ticket.subject.ilike(term),
                    Ticket.description.ilike(term),
                    Customer.full_name.ilike(term),
                    Customer.email.ilike(term),
                )
            )

        # Total count for pagination
        count_stmt = select(func.count()).select_from(query.subquery())
        total_filtered = (await db.execute(count_stmt)).scalar() or 0

        # Pagination and sorting
        offset = (max(1, page) - 1) * limit
        query = query.order_by(desc(Ticket.created_at)).limit(limit).offset(offset)

        rows = (await db.execute(query)).all()

        items: List[TicketListItem] = []
        for t, c, u, tc, voice_id in rows:
            items.append(
                TicketListItem(
                    id=t.id,
                    ticket_number=t.ticket_number,
                    channel=t.channel,
                    status=t.status,
                    priority=t.priority,
                    urgency=t.urgency,
                    sentiment=t.sentiment,
                    subject=t.subject,
                    customer_id=c.id,
                    customer_name=c.full_name,
                    customer_email=c.email,
                    customer_segment=c.segment,
                    assigned_user_id=u.id if u else None,
                    assigned_user_name=u.full_name if u else None,
                    category=tc.category if tc else None,
                    severity=tc.severity if tc else None,
                    has_voice=voice_id is not None,
                    reopened_count=t.reopened_count,
                    sla_due_at=t.sla_due_at,
                    resolved_at=t.resolved_at,
                    closed_at=t.closed_at,
                    created_at=t.created_at,
                    updated_at=t.updated_at
                )
            )

        pages = (total_filtered + limit - 1) // limit if total_filtered > 0 else 1

        return TicketListResponse(
            items=items,
            total=total_filtered,
            page=page,
            limit=limit,
            pages=pages,
            status_counts=status_counts
        )

    @staticmethod
    async def get_ticket_detail(
        db: AsyncSession,
        organization_id: str,
        ticket_id: str
    ) -> TicketDetailResponse:
        """Retrieve complete ticket detail workspace with customer, messages, orders, and investigation."""
        stmt = (
            select(Ticket)
            .options(
                selectinload(Ticket.customer),
                selectinload(Ticket.assigned_user),
                selectinload(Ticket.messages),
                selectinload(Ticket.attachments),
                selectinload(Ticket.classification),
                selectinload(Ticket.voice_transcript),
                selectinload(Ticket.entities),
                selectinload(Ticket.investigation).selectinload(Investigation.events)
            )
            .where(
                and_(
                    Ticket.organization_id == organization_id,
                    Ticket.id == ticket_id
                )
            )
        )
        res = await db.execute(stmt)
        ticket = res.scalar_one_or_none()
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket '{ticket_id}' not found in this organization."
            )

        # Find linked order and payment if any
        order_summary: Optional[OrderSummary] = None
        payment_summary: Optional[PaymentSummary] = None

        # Check extracted entities for order_id or txn_id
        order_num = next((e.entity_value for e in ticket.entities if e.entity_type == "order_id"), None)
        txn_num = next((e.entity_value for e in ticket.entities if e.entity_type == "transaction_id"), None)

        if order_num:
            ord_res = await db.execute(
                select(Order).where(
                    and_(
                        Order.organization_id == organization_id,
                        Order.order_number == order_num
                    )
                )
            )
            ord_obj = ord_res.scalar_one_or_none()
            if ord_obj:
                order_summary = OrderSummary(
                    id=ord_obj.id,
                    order_number=ord_obj.order_number,
                    status=ord_obj.status,
                    total_amount=float(ord_obj.total_amount),
                    currency=ord_obj.currency,
                    items_json=ord_obj.items_json,
                    shipping_address=ord_obj.shipping_address,
                    created_at=ord_obj.created_at
                )

        if txn_num:
            pay_res = await db.execute(
                select(Payment).where(
                    and_(
                        Payment.organization_id == organization_id,
                        Payment.transaction_id == txn_num
                    )
                )
            )
            pay_obj = pay_res.scalar_one_or_none()
            if pay_obj:
                payment_summary = PaymentSummary(
                    id=pay_obj.id,
                    transaction_id=pay_obj.transaction_id,
                    provider=pay_obj.provider,
                    status=pay_obj.status,
                    amount=float(pay_obj.amount),
                    currency=pay_obj.currency,
                    failure_code=pay_obj.failure_code,
                    correlation_id=pay_obj.correlation_id,
                    created_at=pay_obj.created_at
                )

        # Allowed transitions from current state
        allowed = TicketStateMachine.get_allowed_transitions(ticket.status)

        # Investigation summary
        inv_summary: Optional[InvestigationSummaryResponse] = None
        if ticket.investigation:
            inv = ticket.investigation
            inv_summary = InvestigationSummaryResponse(
                id=inv.id,
                status=inv.status,
                summary=inv.summary,
                root_cause_hypothesis=inv.root_cause_hypothesis,
                expected_state_json=inv.expected_state_json,
                actual_state_json=inv.actual_state_json,
                discrepancy=inv.discrepancy,
                verified_facts_json=inv.verified_facts_json,
                assumptions_json=inv.assumptions_json,
                recommended_action=inv.recommended_action,
                confidence=inv.confidence,
                events_count=len(inv.events)
            )

        return TicketDetailResponse(
            id=ticket.id,
            organization_id=ticket.organization_id,
            ticket_number=ticket.ticket_number,
            channel=ticket.channel,
            status=ticket.status,
            priority=ticket.priority,
            urgency=ticket.urgency,
            sentiment=ticket.sentiment,
            subject=ticket.subject,
            description=ticket.description,
            assigned_user_id=ticket.assigned_user_id,
            assigned_user_name=ticket.assigned_user.full_name if ticket.assigned_user else None,
            assigned_agent_id=ticket.assigned_agent_id,
            reopened_count=ticket.reopened_count,
            sla_due_at=ticket.sla_due_at,
            resolved_at=ticket.resolved_at,
            closed_at=ticket.closed_at,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            customer=CustomerSummary.model_validate(ticket.customer),
            messages=[MessageResponse.model_validate(m) for m in ticket.messages],
            attachments=[AttachmentResponse.model_validate(a) for a in ticket.attachments],
            classification=ClassificationResponse.model_validate(ticket.classification) if ticket.classification else None,
            voice_transcript=VoiceTranscriptResponse.model_validate(ticket.voice_transcript) if ticket.voice_transcript else None,
            entities=[ExtractedEntityResponse.model_validate(e) for e in ticket.entities],
            investigation=inv_summary,
            order=order_summary,
            payment=payment_summary,
            allowed_transitions=allowed
        )

    @staticmethod
    async def transition_status(
        db: AsyncSession,
        organization_id: str,
        ticket_id: str,
        actor_id: str,
        actor_name: str,
        target_status: str,
        reason: Optional[str] = None
    ) -> Ticket:
        """Enforces ticket state machine, updates timestamps, handles reopening, and logs audit event."""
        stmt = select(Ticket).where(
            and_(
                Ticket.organization_id == organization_id,
                Ticket.id == ticket_id
            )
        )
        res = await db.execute(stmt)
        ticket = res.scalar_one_or_none()
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found.")

        old_status = ticket.status
        target_status = target_status.lower()

        # Validate against State Machine
        TicketStateMachine.validate_transition(old_status, target_status)

        now = datetime.now(timezone.utc)
        ticket.status = target_status
        ticket.updated_at = now

        # Reopen logic
        if old_status in [TicketStatus.RESOLVED.value, TicketStatus.CLOSED.value] and target_status == TicketStatus.INVESTIGATING.value:
            ticket.reopened_count += 1
            ticket.resolved_at = None
            ticket.closed_at = None

        if target_status == TicketStatus.RESOLVED.value:
            ticket.resolved_at = now
        elif target_status == TicketStatus.CLOSED.value:
            ticket.closed_at = now

        # Record in audit log
        await AuditService.log_event(
            db=db,
            organization_id=organization_id,
            actor_type="user",
            actor_id=actor_id,
            actor_name=actor_name,
            action="ticket.status_change",
            entity_type="ticket",
            entity_id=ticket.id,
            old_state={"status": old_status},
            new_state={"status": target_status, "reason": reason, "reopened_count": ticket.reopened_count}
        )

        await db.flush()
        return ticket

    @staticmethod
    async def assign_ticket(
        db: AsyncSession,
        organization_id: str,
        ticket_id: str,
        actor_id: str,
        actor_name: str,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> Ticket:
        """Assign ticket to a human user or an AI agent."""
        stmt = select(Ticket).where(
            and_(
                Ticket.organization_id == organization_id,
                Ticket.id == ticket_id
            )
        )
        res = await db.execute(stmt)
        ticket = res.scalar_one_or_none()
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found.")

        old_user = ticket.assigned_user_id
        old_agent = ticket.assigned_agent_id

        if user_id is not None:
            if user_id != "":
                user_res = await db.execute(
                    select(User).where(
                        and_(
                            User.organization_id == organization_id,
                            User.id == user_id
                        )
                    )
                )
                if not user_res.scalar_one_or_none():
                    raise HTTPException(status_code=400, detail=f"User '{user_id}' not found in this organization.")
                ticket.assigned_user_id = user_id
            else:
                ticket.assigned_user_id = None

        if agent_id is not None:
            ticket.assigned_agent_id = agent_id if agent_id != "" else None

        ticket.updated_at = datetime.now(timezone.utc)

        await AuditService.log_event(
            db=db,
            organization_id=organization_id,
            actor_type="user",
            actor_id=actor_id,
            actor_name=actor_name,
            action="ticket.assigned",
            entity_type="ticket",
            entity_id=ticket.id,
            old_state={"assigned_user_id": old_user, "assigned_agent_id": old_agent},
            new_state={"assigned_user_id": ticket.assigned_user_id, "assigned_agent_id": ticket.assigned_agent_id}
        )

        await db.flush()
        return ticket

    @staticmethod
    async def add_message(
        db: AsyncSession,
        organization_id: str,
        ticket_id: str,
        actor_id: Optional[str],
        actor_name: Optional[str],
        sender_type: str,  # customer, user, agent
        content: str,
        is_internal_note: bool = False,
        language: str = "en"
    ) -> TicketMessage:
        """Add a reply or internal note. Resumes investigation if waiting for customer and customer replies."""
        stmt = select(Ticket).where(
            and_(
                Ticket.organization_id == organization_id,
                Ticket.id == ticket_id
            )
        )
        res = await db.execute(stmt)
        ticket = res.scalar_one_or_none()
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found.")

        clean_content = mask_pii_for_prompts(content)
        now = datetime.now(timezone.utc)

        msg = TicketMessage(
            ticket_id=ticket.id,
            sender_type=sender_type,
            sender_id=actor_id,
            content=clean_content,
            language=language,
            is_internal_note=is_internal_note,
            created_at=now
        )
        db.add(msg)

        # If waiting for customer and customer sends a response, transition back to investigating!
        if sender_type == "customer" and ticket.status == TicketStatus.WAITING_FOR_CUSTOMER.value:
            ticket.status = TicketStatus.INVESTIGATING.value
            await AuditService.log_event(
                db=db,
                organization_id=organization_id,
                actor_type="customer",
                actor_id=actor_id,
                actor_name=actor_name or "Customer",
                action="ticket.status_change",
                entity_type="ticket",
                entity_id=ticket.id,
                old_state={"status": TicketStatus.WAITING_FOR_CUSTOMER.value},
                new_state={"status": TicketStatus.INVESTIGATING.value, "trigger": "customer_reply"}
            )

        ticket.updated_at = now

        await AuditService.log_event(
            db=db,
            organization_id=organization_id,
            actor_type="user" if sender_type == "user" else ("agent" if sender_type == "agent" else "customer"),
            actor_id=actor_id,
            actor_name=actor_name,
            action="ticket.note_added" if is_internal_note else "ticket.message_sent",
            entity_type="ticket",
            entity_id=ticket.id,
            new_state={"is_internal_note": is_internal_note, "length": len(clean_content)}
        )

        await db.flush()
        return msg

    @staticmethod
    async def add_attachment(
        db: AsyncSession,
        organization_id: str,
        ticket_id: str,
        actor_id: str,
        actor_name: str,
        upload_file: UploadFile
    ) -> TicketAttachment:
        """Attach a file to the ticket."""
        stmt = select(Ticket).where(
            and_(
                Ticket.organization_id == organization_id,
                Ticket.id == ticket_id
            )
        )
        res = await db.execute(stmt)
        ticket = res.scalar_one_or_none()
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found.")

        ext = os.path.splitext(upload_file.filename or "file")[1]
        stored_name = f"{ticket.id}_{uuid.uuid4().hex[:8]}{ext}"
        storage_path = os.path.join(settings.STORAGE_DIR, "attachments", stored_name)

        content = await upload_file.read()
        with open(storage_path, "wb") as f:
            f.write(content)

        attachment = TicketAttachment(
            ticket_id=ticket.id,
            file_name=upload_file.filename or stored_name,
            file_type=upload_file.content_type or "application/octet-stream",
            file_size=len(content),
            storage_url=f"/storage/attachments/{stored_name}",
            created_at=datetime.now(timezone.utc)
        )
        db.add(attachment)

        await AuditService.log_event(
            db=db,
            organization_id=organization_id,
            actor_type="user",
            actor_id=actor_id,
            actor_name=actor_name,
            action="ticket.attachment_added",
            entity_type="ticket",
            entity_id=ticket.id,
            new_state={"file_name": attachment.file_name, "file_size": attachment.file_size}
        )

        await db.flush()
        return attachment
