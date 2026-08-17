from app.schemas.document_search import UserRole
from app.security.auth import CognitoTokenVerifier


def test_cognito_customer_group_becomes_customer_role():
    claims = {
        "sub": "user-123",
        "username": "customer@example.com",
        "client_id": "client-123",
        "cognito:groups": [
            "customer",
        ],
    }

    principal = (
        CognitoTokenVerifier._principal_from_claims(
            claims
        )
    )

    assert principal.subject == "user-123"

    assert (
        principal.username
        == "customer@example.com"
    )

    assert (
        principal.client_id
        == "client-123"
    )

    assert principal.roles == [
        UserRole.CUSTOMER,
    ]


def test_multiple_cognito_groups_become_multiple_roles():
    claims = {
        "sub": "user-456",
        "username": "dealer@example.com",
        "client_id": "client-123",
        "cognito:groups": [
            "dealer",
            "support",
        ],
    }

    principal = (
        CognitoTokenVerifier._principal_from_claims(
            claims
        )
    )

    assert principal.roles == [
        UserRole.DEALER,
        UserRole.SUPPORT,
    ]


def test_unknown_cognito_groups_are_ignored():
    claims = {
        "sub": "user-789",
        "username": "dealer@example.com",
        "client_id": "client-123",
        "cognito:groups": [
            "dealer",
            "some-unknown-group",
            "another-unknown-group",
        ],
    }

    principal = (
        CognitoTokenVerifier._principal_from_claims(
            claims
        )
    )

    assert principal.roles == [
        UserRole.DEALER,
    ]


def test_user_with_only_unknown_groups_has_no_roles():
    claims = {
        "sub": "user-999",
        "username": "unknown@example.com",
        "client_id": "client-123",
        "cognito:groups": [
            "unknown-group",
        ],
    }

    principal = (
        CognitoTokenVerifier._principal_from_claims(
            claims
        )
    )

    assert principal.roles == []


def test_missing_groups_results_in_empty_roles():
    claims = {
        "sub": "user-111",
        "username": "nogroups@example.com",
        "client_id": "client-123",
    }

    principal = (
        CognitoTokenVerifier._principal_from_claims(
            claims
        )
    )

    assert principal.roles == []


def test_duplicate_groups_are_deduplicated():
    claims = {
        "sub": "user-222",
        "username": "admin@example.com",
        "client_id": "client-123",
        "cognito:groups": [
            "admin",
            "admin",
            "support",
            "support",
        ],
    }

    principal = (
        CognitoTokenVerifier._principal_from_claims(
            claims
        )
    )

    assert principal.roles == [
        UserRole.ADMIN,
        UserRole.SUPPORT,
    ]


def test_cognito_username_claim_is_supported():
    claims = {
        "sub": "user-333",
        "cognito:username": "cognito-user",
        "client_id": "client-123",
        "cognito:groups": [
            "customer",
        ],
    }

    principal = (
        CognitoTokenVerifier._principal_from_claims(
            claims
        )
    )

    assert (
        principal.username
        == "cognito-user"
    )


def test_username_claim_takes_precedence():
    claims = {
        "sub": "user-444",
        "username": "preferred-username",
        "cognito:username": "fallback-username",
        "client_id": "client-123",
        "cognito:groups": [
            "customer",
        ],
    }

    principal = (
        CognitoTokenVerifier._principal_from_claims(
            claims
        )
    )

    assert (
        principal.username
        == "preferred-username"
    )