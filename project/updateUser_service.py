from enum import Enum
from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class UserRole(Enum):
    """
    Enum defining the possible roles: ADMIN, PROFESSIONAL, and END_USER.
    """

    ADMIN: str
    PROFESSIONAL: str
    END_USER: str


class User(BaseModel):
    """
    Details of the user following the update.
    """

    id: str
    username: str
    role: UserRole


class UpdateUserDetailsResponse(BaseModel):
    """
    Provides feedback on the operation's success and returns the updated user details.
    """

    success: bool
    user: User


async def updateUser(
    userId: str, username: Optional[str], password: Optional[str]
) -> UpdateUserDetailsResponse:
    """
    Updates a user's details. Administrators can change roles, statuses, or other pertinent user information as necessary through this endpoint.

    Args:
        userId (str): Unique identifier of the user to be updated, extracted from the URL path.
        username (Optional[str]): New username for the user. Optional field.
        password (Optional[str]): New password for the user. Optional field and should be hashed and processed securely.

    Returns:
        UpdateUserDetailsResponse: Provides feedback on the operation's success and returns the updated user details.
    """
    user = await prisma.models.User.prisma().find_unique(where={"id": userId})
    if user is None:
        return UpdateUserDetailsResponse(success=False, user=None)
    update_data = {}
    if username is not None:
        update_data["username"] = username
    if password is not None:
        update_data["password"] = password
    updated_user = await prisma.models.User.prisma().update(
        where={"id": user.id}, data=update_data, include={"role": True}
    )
    if updated_user:
        return_user = User(
            id=updated_user.id, username=updated_user.username, role=updated_user.role
        )  # TODO(autogpt): Cannot access member "username" for type "User"
        #     Member "username" is unknown. reportAttributeAccessIssue
        return UpdateUserDetailsResponse(success=True, user=return_user)
    else:
        return UpdateUserDetailsResponse(success=False, user=None)
