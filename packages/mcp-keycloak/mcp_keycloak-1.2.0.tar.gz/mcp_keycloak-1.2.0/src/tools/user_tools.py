from typing import Dict, Any, Optional, List
from ..common.server import mcp
from .keycloak_client import KeycloakClient


client = KeycloakClient()


@mcp.tool()
async def list_users(
    first: Optional[int] = None,
    max: Optional[int] = None,
    search: Optional[str] = None,
    username: Optional[str] = None,
    email: Optional[str] = None,
    enabled: Optional[bool] = None,
    realm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List users in the realm.

    Args:
        first: Pagination offset
        max: Maximum results size (defaults to 100)
        search: Search string for username, first/last name, or email
        username: Username filter
        email: Email filter
        enabled: Filter by enabled/disabled users
        realm: Target realm (uses default if not specified)

    Returns:
        List of user objects
    """
    params = {}
    if first is not None:
        params["first"] = first
    if max is not None:
        params["max"] = max
    if search:
        params["search"] = search
    if username:
        params["username"] = username
    if email:
        params["email"] = email
    if enabled is not None:
        params["enabled"] = str(enabled).lower()

    return await client._make_request("GET", "/users", params=params, realm=realm)


@mcp.tool()
async def get_user(user_id: str, realm: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a specific user by ID.

    Args:
        user_id: The user's ID
        realm: Target realm (uses default if not specified)

    Returns:
        User object
    """
    return await client._make_request("GET", f"/users/{user_id}", realm=realm)


@mcp.tool()
async def create_user(
    username: str,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    enabled: bool = True,
    email_verified: bool = False,
    temporary_password: Optional[str] = None,
    attributes: Optional[Dict[str, List[str]]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create a new user.

    Args:
        username: Username for the new user
        email: Email address
        first_name: First name
        last_name: Last name
        enabled: Whether the user is enabled
        email_verified: Whether the email is verified
        temporary_password: Initial password (user will be required to change it)
        attributes: Additional user attributes
        realm: Target realm (uses default if not specified)

    Returns:
        Dict with status and location of created user
    """
    user_data = {
        "username": username,
        "enabled": enabled,
        "emailVerified": email_verified,
    }

    if email:
        user_data["email"] = email
    if first_name:
        user_data["firstName"] = first_name
    if last_name:
        user_data["lastName"] = last_name
    if attributes:
        user_data["attributes"] = attributes

    if temporary_password:
        user_data["credentials"] = [
            {"type": "password", "value": temporary_password, "temporary": True}
        ]

    # Create user returns no content, but includes Location header
    await client._make_request("POST", "/users", data=user_data, realm=realm)
    return {"status": "created", "message": f"User {username} created successfully"}


@mcp.tool()
async def update_user(
    user_id: str,
    username: Optional[str] = None,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    enabled: Optional[bool] = None,
    email_verified: Optional[bool] = None,
    attributes: Optional[Dict[str, List[str]]] = None,
    realm: Optional[str] = None,
) -> Dict[str, str]:
    """
    Update an existing user.

    Args:
        user_id: The user's ID
        username: New username
        email: New email address
        first_name: New first name
        last_name: New last name
        enabled: Whether the user is enabled
        email_verified: Whether the email is verified
        attributes: Updated user attributes
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    # First get the current user data
    current_user = await client._make_request("GET", f"/users/{user_id}", realm=realm)

    # Update only provided fields
    if username is not None:
        current_user["username"] = username
    if email is not None:
        current_user["email"] = email
    if first_name is not None:
        current_user["firstName"] = first_name
    if last_name is not None:
        current_user["lastName"] = last_name
    if enabled is not None:
        current_user["enabled"] = enabled
    if email_verified is not None:
        current_user["emailVerified"] = email_verified
    if attributes is not None:
        current_user["attributes"] = attributes

    await client._make_request(
        "PUT", f"/users/{user_id}", data=current_user, realm=realm
    )
    return {"status": "updated", "message": f"User {user_id} updated successfully"}


@mcp.tool()
async def delete_user(user_id: str, realm: Optional[str] = None) -> Dict[str, str]:
    """
    Delete a user.

    Args:
        user_id: The user's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request("DELETE", f"/users/{user_id}", realm=realm)
    return {"status": "deleted", "message": f"User {user_id} deleted successfully"}


@mcp.tool()
async def reset_user_password(
    user_id: str, password: str, temporary: bool = True, realm: Optional[str] = None
) -> Dict[str, str]:
    """
    Reset a user's password.

    Args:
        user_id: The user's ID
        password: New password
        temporary: Whether the password is temporary (user must change on next login)
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    credential_data = {"type": "password", "value": password, "temporary": temporary}

    await client._make_request(
        "PUT", f"/users/{user_id}/reset-password", data=credential_data, realm=realm
    )
    return {"status": "success", "message": f"Password reset for user {user_id}"}


@mcp.tool()
async def get_user_sessions(
    user_id: str, realm: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get active sessions for a user.

    Args:
        user_id: The user's ID
        realm: Target realm (uses default if not specified)

    Returns:
        List of active sessions
    """
    return await client._make_request("GET", f"/users/{user_id}/sessions", realm=realm)


@mcp.tool()
async def logout_user(user_id: str, realm: Optional[str] = None) -> Dict[str, str]:
    """
    Logout all sessions for a user.

    Args:
        user_id: The user's ID
        realm: Target realm (uses default if not specified)

    Returns:
        Status message
    """
    await client._make_request("POST", f"/users/{user_id}/logout", realm=realm)
    return {
        "status": "success",
        "message": f"User {user_id} logged out from all sessions",
    }


@mcp.tool()
async def count_users(realm: Optional[str] = None) -> int:
    """
    Count all users.

    Args:
        realm: Target realm (uses default if not specified)

    Returns:
        Number of users
    """
    return await client._make_request("GET", "/users/count", realm=realm)
