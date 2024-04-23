import datetime
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


class UserDetailsResponse(BaseModel):
    """
    Response model containing detailed information of a specific user.
    """

    username: str
    role: UserRole
    activity_status: str


async def getUserDetails(userId: str) -> UserDetailsResponse:
    """
    Fetches detailed information of a specific user by user ID. It returns data such as username, user role,
    and activity status. The prisma.models.User Database is queried to retrieve this data.

    Args:
        userId (str): The unique identifier of the user.

    Returns:
        UserDetailsResponse: Response model containing detailed information of a specific user.
    """
    user: Optional[prisma.models.User] = await prisma.models.User.prisma().find_unique(
        where={"id": userId}
    )
    if user is None:
        raise ValueError(f"No user found with ID {userId}")
    activity_status = "offline"
    if user.lastLogin is not None:
        time_diff = datetime.datetime.utcnow() - user.lastLogin
        if time_diff.total_seconds() < 600:
            activity_status = "online"
    return UserDetailsResponse(
        username=user.email, role=UserRole[user.role], activity_status=activity_status
    )
