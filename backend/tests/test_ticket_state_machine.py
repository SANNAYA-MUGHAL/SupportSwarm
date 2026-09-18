import pytest
from fastapi import HTTPException
from app.core.state_machine import TicketStateMachine, TicketStatus

def test_valid_forward_transitions():
    # New -> Triaged
    assert TicketStateMachine.is_transition_allowed(TicketStatus.NEW.value, TicketStatus.TRIAGED.value) is True
    # Triaged -> Investigating
    assert TicketStateMachine.is_transition_allowed(TicketStatus.TRIAGED.value, TicketStatus.INVESTIGATING.value) is True
    # Investigating -> Waiting for Approval
    assert TicketStateMachine.is_transition_allowed(TicketStatus.INVESTIGATING.value, TicketStatus.WAITING_FOR_APPROVAL.value) is True
    # Waiting for Approval -> Waiting for Customer
    assert TicketStateMachine.is_transition_allowed(TicketStatus.WAITING_FOR_APPROVAL.value, TicketStatus.WAITING_FOR_CUSTOMER.value) is True
    # Waiting for Customer -> Resolved
    assert TicketStateMachine.is_transition_allowed(TicketStatus.WAITING_FOR_CUSTOMER.value, TicketStatus.RESOLVED.value) is True
    # Resolved -> Closed
    assert TicketStateMachine.is_transition_allowed(TicketStatus.RESOLVED.value, TicketStatus.CLOSED.value) is True

def test_reopen_transitions():
    # Resolved -> Investigating (Reopened)
    assert TicketStateMachine.is_transition_allowed(TicketStatus.RESOLVED.value, TicketStatus.INVESTIGATING.value) is True
    # Closed -> Investigating (Reopened)
    assert TicketStateMachine.is_transition_allowed(TicketStatus.CLOSED.value, TicketStatus.INVESTIGATING.value) is True

def test_illegal_transitions_raise_400():
    # Closed cannot transition directly to New
    with pytest.raises(HTTPException) as exc_info:
        TicketStateMachine.validate_transition(TicketStatus.CLOSED.value, TicketStatus.NEW.value)
    assert exc_info.value.status_code == 400
    assert "Illegal state transition" in exc_info.value.detail

    # Resolved cannot transition directly to Triaged
    with pytest.raises(HTTPException) as exc_info2:
        TicketStateMachine.validate_transition(TicketStatus.RESOLVED.value, TicketStatus.TRIAGED.value)
    assert exc_info2.value.status_code == 400

    # New cannot jump directly to Resolved without investigation
    with pytest.raises(HTTPException) as exc_info3:
        TicketStateMachine.validate_transition(TicketStatus.NEW.value, TicketStatus.RESOLVED.value)
    assert exc_info3.value.status_code == 400

def test_allowed_transitions_list():
    allowed_from_new = TicketStateMachine.get_allowed_transitions(TicketStatus.NEW.value)
    assert TicketStatus.TRIAGED.value in allowed_from_new
    assert TicketStatus.INVESTIGATING.value in allowed_from_new
    assert TicketStatus.RESOLVED.value not in allowed_from_new

    allowed_from_resolved = TicketStateMachine.get_allowed_transitions(TicketStatus.RESOLVED.value)
    assert TicketStatus.CLOSED.value in allowed_from_resolved
    assert TicketStatus.INVESTIGATING.value in allowed_from_resolved
