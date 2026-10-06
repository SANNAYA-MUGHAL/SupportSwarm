from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.auth import CurrentUser
from app.schemas.ticket import (
    TicketCreate, TicketListResponse, TicketDetailResponse,
    TicketStateTransitionRequest, TicketAssignmentRequest,
    MessageCreateRequest, MessageResponse, AttachmentResponse
)
from app.schemas.audit import AuditEventResponse
from app.services.ticket_service import TicketService
from app.services.audit_service import AuditService
from app.services.auth_service import get_current_user
from app.core.rbac import require_roles, has_permission, UserRole, Permission

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.get("", response_model=TicketListResponse, status_code=status.HTTP_200_OK)
async def list_tickets(
    status: Optional[str] = Query(None, description="Filter by ticket status or 'all'"),
    channel: Optional[str] = Query(None, description="Filter by channel"),
    severity: Optional[str] = Query(None, description="Filter by severity (S1, S2, S3, S4)"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    category: Optional[str] = Query(None, description="Filter by category"),
    assignee: Optional[str] = Query(None, description="Filter by assignee ('unassigned', 'me', or user_id)"),
    search: Optional[str] = Query(None, description="Full text search across number, subject, customer"),
    page: int = Query(1, ge=1),
    limit: int = Query(15, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """List tickets with status tab counts, multi-field filtering, and pagination."""
    return await TicketService.list_tickets(
        db=db,
        organization_id=current_user.organization_id,
        status_filter=status,
        channel=channel,
        severity=severity,
        priority=priority,
        category=category,
        assignee=assignee,
        search=search,
        page=page,
        limit=limit,
        current_user_id=current_user.user_id
    )

@router.post("", response_model=TicketDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    payload: TicketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Create a ticket via manual entry, customer support form, or simulated email."""
    ticket = await TicketService.create_ticket(
        db=db,
        organization_id=current_user.organization_id,
        actor_id=current_user.user_id,
        actor_name=current_user.full_name,
        payload=payload
    )
    return await TicketService.get_ticket_detail(
        db=db,
        organization_id=current_user.organization_id,
        ticket_id=ticket.id
    )

@router.post("/voice", response_model=TicketDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_voice_ticket(
    customer_name: str = Form(...),
    customer_email: str = Form(...),
    customer_phone: Optional[str] = Form(None),
    subject: str = Form(...),
    description: str = Form(...),
    priority: str = Form("s2_high"),
    category: str = Form("payment_pending"),
    order_number: Optional[str] = Form(None),
    audio_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Ingest a customer voice note (MP3, WAV, M4A, OGG) and create a structured ticket."""
    payload = TicketCreate(
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        channel="voice_note",
        subject=subject,
        description=description,
        priority=priority,
        category=category,
        order_number=order_number
    )
    ticket = await TicketService.create_ticket(
        db=db,
        organization_id=current_user.organization_id,
        actor_id=current_user.user_id,
        actor_name=current_user.full_name,
        payload=payload,
        audio_file=audio_file
    )
    return await TicketService.get_ticket_detail(
        db=db,
        organization_id=current_user.organization_id,
        ticket_id=ticket.id
    )

@router.get("/{ticket_id}", response_model=TicketDetailResponse, status_code=status.HTTP_200_OK)
async def get_ticket(
    ticket_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Retrieve complete ticket detail workspace."""
    return await TicketService.get_ticket_detail(
        db=db,
        organization_id=current_user.organization_id,
        ticket_id=ticket_id
    )

@router.patch("/{ticket_id}/status", response_model=TicketDetailResponse, status_code=status.HTTP_200_OK)
async def transition_ticket_status(
    ticket_id: str,
    payload: TicketStateTransitionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Enforce ticket state machine transition with audit logging."""
    # Viewers cannot transition tickets
    require_roles(
        [UserRole.ADMIN, UserRole.SUPPORT_LEAD, UserRole.SUPPORT_AGENT, UserRole.QA_ENGINEER, UserRole.PRODUCT_MANAGER],
        current_user.role
    )
    await TicketService.transition_status(
        db=db,
        organization_id=current_user.organization_id,
        ticket_id=ticket_id,
        actor_id=current_user.user_id,
        actor_name=current_user.full_name,
        target_status=payload.target_status,
        reason=payload.reason
    )
    return await TicketService.get_ticket_detail(
        db=db,
        organization_id=current_user.organization_id,
        ticket_id=ticket_id
    )

@router.patch("/{ticket_id}/assign", response_model=TicketDetailResponse, status_code=status.HTTP_200_OK)
async def assign_ticket(
    ticket_id: str,
    payload: TicketAssignmentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Assign ticket to a team member or AI agent."""
    require_roles(
        [UserRole.ADMIN, UserRole.SUPPORT_LEAD, UserRole.SUPPORT_AGENT],
        current_user.role
    )
    await TicketService.assign_ticket(
        db=db,
        organization_id=current_user.organization_id,
        ticket_id=ticket_id,
        actor_id=current_user.user_id,
        actor_name=current_user.full_name,
        user_id=payload.user_id,
        agent_id=payload.agent_id
    )
    return await TicketService.get_ticket_detail(
        db=db,
        organization_id=current_user.organization_id,
        ticket_id=ticket_id
    )

@router.post("/{ticket_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_message(
    ticket_id: str,
    payload: MessageCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Add a customer reply or internal note to the ticket stream."""
    require_roles(
        [UserRole.ADMIN, UserRole.SUPPORT_LEAD, UserRole.SUPPORT_AGENT, UserRole.QA_ENGINEER, UserRole.PRODUCT_MANAGER],
        current_user.role
    )
    return await TicketService.add_message(
        db=db,
        organization_id=current_user.organization_id,
        ticket_id=ticket_id,
        actor_id=current_user.user_id,
        actor_name=current_user.full_name,
        sender_type="user",
        content=payload.content,
        is_internal_note=payload.is_internal_note,
        language=payload.language
    )

@router.post("/{ticket_id}/attachments", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def add_attachment(
    ticket_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Upload and attach a file to the ticket."""
    require_roles(
        [UserRole.ADMIN, UserRole.SUPPORT_LEAD, UserRole.SUPPORT_AGENT],
        current_user.role
    )
    return await TicketService.add_attachment(
        db=db,
        organization_id=current_user.organization_id,
        ticket_id=ticket_id,
        actor_id=current_user.user_id,
        actor_name=current_user.full_name,
        upload_file=file
    )

@router.get("/{ticket_id}/audit", response_model=List[AuditEventResponse], status_code=status.HTTP_200_OK)
async def get_ticket_audit(
    ticket_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Retrieve audit events for a specific ticket."""
    return await AuditService.get_ticket_audit_logs(
        db=db,
        organization_id=current_user.organization_id,
        ticket_id=ticket_id
    )

