from enum import Enum
from typing import Set, Dict, List
from fastapi import HTTPException, status

class TicketStatus(str, Enum):
    NEW = "new"
    TRIAGED = "triaged"
    INVESTIGATING = "investigating"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    WAITING_FOR_CUSTOMER = "waiting_for_customer"
    WAITING_FOR_INTERNAL_TEAM = "waiting_for_internal_team"
    RESOLVED = "resolved"
    CLOSED = "closed"

# Explicit allowed state transition map
ALLOWED_TRANSITIONS: Dict[TicketStatus, Set[TicketStatus]] = {
    TicketStatus.NEW: {
        TicketStatus.TRIAGED,
        TicketStatus.INVESTIGATING,
        TicketStatus.WAITING_FOR_CUSTOMER,
        TicketStatus.WAITING_FOR_INTERNAL_TEAM,
        TicketStatus.CLOSED,
    },
    TicketStatus.TRIAGED: {
        TicketStatus.INVESTIGATING,
        TicketStatus.WAITING_FOR_APPROVAL,
        TicketStatus.WAITING_FOR_CUSTOMER,
        TicketStatus.WAITING_FOR_INTERNAL_TEAM,
        TicketStatus.CLOSED,
    },
    TicketStatus.INVESTIGATING: {
        TicketStatus.WAITING_FOR_APPROVAL,
        TicketStatus.WAITING_FOR_CUSTOMER,
        TicketStatus.WAITING_FOR_INTERNAL_TEAM,
        TicketStatus.RESOLVED,
        TicketStatus.CLOSED,
    },
    TicketStatus.WAITING_FOR_APPROVAL: {
        TicketStatus.WAITING_FOR_CUSTOMER,
        TicketStatus.WAITING_FOR_INTERNAL_TEAM,
        TicketStatus.INVESTIGATING,
        TicketStatus.RESOLVED,
        TicketStatus.CLOSED,
    },
    TicketStatus.WAITING_FOR_CUSTOMER: {
        TicketStatus.INVESTIGATING,
        TicketStatus.WAITING_FOR_INTERNAL_TEAM,
        TicketStatus.WAITING_FOR_APPROVAL,
        TicketStatus.RESOLVED,
        TicketStatus.CLOSED,
    },
    TicketStatus.WAITING_FOR_INTERNAL_TEAM: {
        TicketStatus.INVESTIGATING,
        TicketStatus.WAITING_FOR_APPROVAL,
        TicketStatus.WAITING_FOR_CUSTOMER,
        TicketStatus.RESOLVED,
        TicketStatus.CLOSED,
    },
    TicketStatus.RESOLVED: {
        TicketStatus.CLOSED,
        TicketStatus.INVESTIGATING,  # Reopened by customer or agent
    },
    TicketStatus.CLOSED: {
        TicketStatus.INVESTIGATING,  # Reopened by customer or agent
    },
}

class TicketStateMachine:
    @staticmethod
    def is_transition_allowed(current_status: str, target_status: str) -> bool:
        try:
            curr = TicketStatus(current_status)
            target = TicketStatus(target_status)
        except ValueError:
            return False

        if curr == target:
            return True

        allowed = ALLOWED_TRANSITIONS.get(curr, set())
        return target in allowed

    @staticmethod
    def get_allowed_transitions(current_status: str) -> List[str]:
        try:
            curr = TicketStatus(current_status)
            return [s.value for s in ALLOWED_TRANSITIONS.get(curr, set())]
        except ValueError:
            return []

    @staticmethod
    def validate_transition(current_status: str, target_status: str):
        if not TicketStateMachine.is_transition_allowed(current_status, target_status):
            allowed = TicketStateMachine.get_allowed_transitions(current_status)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Illegal state transition from '{current_status}' to '{target_status}'. Allowed next states: {allowed}"
            )
