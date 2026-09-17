import pytest
from datetime import timedelta
from fastapi import HTTPException
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.core.rbac import UserRole, Permission, has_permission, require_roles
from app.core.pii_masking import mask_credit_card, mask_pii_for_prompts, sanitize_payload

def test_password_hashing():
    raw_password = "SecretPassword123!"
    hashed = get_password_hash(raw_password)
    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

def test_jwt_token_encode_decode():
    payload = {"sub": "user-123", "org_id": "org-456", "role": "support_lead"}
    token = create_access_token(payload, expires_delta=timedelta(minutes=30))
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user-123"
    assert decoded["org_id"] == "org-456"
    assert decoded["role"] == "support_lead"
    assert decoded["iss"] == "supportswarm"

def test_jwt_invalid_token():
    invalid_token = "invalid.token.payload"
    decoded = decode_access_token(invalid_token)
    assert decoded is None

def test_rbac_permissions():
    # Admin has all permissions
    assert has_permission(UserRole.ADMIN, Permission.SETTINGS_MANAGE) is True
    assert has_permission(UserRole.ADMIN, Permission.RESPONSES_APPROVE) is True
    assert has_permission(UserRole.ADMIN, Permission.INCIDENTS_DECLARE) is True

    # Support Lead can approve responses and declare incidents, but not manage org settings
    assert has_permission(UserRole.SUPPORT_LEAD, Permission.RESPONSES_APPROVE) is True
    assert has_permission(UserRole.SUPPORT_LEAD, Permission.INCIDENTS_DECLARE) is True
    assert has_permission(UserRole.SUPPORT_LEAD, Permission.SETTINGS_MANAGE) is False

    # Support Agent can read/update tickets and draft responses, but NOT approve responses
    assert has_permission(UserRole.SUPPORT_AGENT, Permission.TICKETS_UPDATE) is True
    assert has_permission(UserRole.SUPPORT_AGENT, Permission.RESPONSES_DRAFT) is True
    assert has_permission(UserRole.SUPPORT_AGENT, Permission.RESPONSES_APPROVE) is False

    # Product Manager has product decision permissions
    assert has_permission(UserRole.PRODUCT_MANAGER, Permission.PRODUCT_DECISION) is True
    assert has_permission(UserRole.SUPPORT_AGENT, Permission.PRODUCT_DECISION) is False

    # QA Engineer has bug creation permissions
    assert has_permission(UserRole.QA_ENGINEER, Permission.BUGS_CREATE) is True
    assert has_permission(UserRole.VIEWER, Permission.BUGS_CREATE) is False

def test_require_roles_enforcement():
    # Allowed role should pass
    require_roles([UserRole.ADMIN, UserRole.SUPPORT_LEAD], "support_lead")
    
    # Disallowed role should raise 403
    with pytest.raises(HTTPException) as exc_info:
        require_roles([UserRole.ADMIN], "support_agent")
    assert exc_info.value.status_code == 403

def test_pii_credit_card_masking():
    text = "My Visa card is 4532 1234 5678 9012 and payment failed."
    masked = mask_credit_card(text)
    assert "4532" not in masked
    assert "9012" in masked
    assert "****-****-****-9012" in masked

def test_pii_for_prompts():
    text = "Customer says: Card is 5425-1234-5678-8888, CVV: 123. Please refund."
    masked = mask_pii_for_prompts(text)
    assert "5425" not in masked
    assert "8888" in masked
    assert "123" not in masked
    assert "CVV: ***" in masked

def test_sanitize_payload():
    data = {
        "user": "Alice",
        "card_number": "4111 2222 3333 4444",
        "secret_token": "xyz123",
        "note": "Payment with card 4111 2222 3333 4444 failed."
    }
    sanitized = sanitize_payload(data)
    assert sanitized["user"] == "Alice"
    assert sanitized["card_number"] == "[REDACTED]"
    assert sanitized["secret_token"] == "[REDACTED]"
    assert "4111" not in sanitized["note"]
    assert "4444" in sanitized["note"]
