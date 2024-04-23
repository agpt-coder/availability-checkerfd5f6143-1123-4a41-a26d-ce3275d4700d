from datetime import datetime
from enum import Enum
from typing import List, Optional

import prisma
import prisma.models
from pydantic import BaseModel


class GetUsersRequest(BaseModel):
    """
    Request parameters for fetching all users. This endpoint does not require any specific request parameters as it is a simple GET request.
    """

    pass


class UserRole(Enum):
    """
    Enum defining the possible roles: ADMIN, PROFESSIONAL, and END_USER.
    """

    ADMIN: str
    PROFESSIONAL: str
    END_USER: str


class UserDetail(BaseModel):
    """
    Detailed information about a user necessary for administrative management. Includes fields relevant to the user's role and professional status if applicable.
    """

    id: str
    email: str
    role: UserRole
    isAvailable: Optional[bool] = None
    lastLogin: Optional[datetime] = None


class UsersResponse(BaseModel):
    """
    This model represents the response which includes a list of users with relevant details required for administrative overview.
    """

    users: List[UserDetail]


async def listUsers(request: GetUsersRequest) -> UsersResponse:
    """
    Retrieves a list of all user profiles. It allows the admin to view all system users, which is essential for
    management and oversight.

    Args:
        request (GetUsersRequest): Request parameters for fetching all users. This endpoint does not require any
        specific request parameters as it is a simple GET request.

    Returns:
        UsersResponse: This model represents the response which includes a list of users with relevant details
        required for administrative overview.
    """
    users_data = await prisma.models.User.prisma().find_many(
        include={"Professional": True}
    )
    users_list = [
        UserDetail(
            id=user.id,
            email=user.email,
            role=user.role,
            isAvailable=user.Professional.isAvailable if user.Professional else None,
            lastLogin=user.lastLogin,
        )
        for user in users_data
    ]
    return UsersResponse(users=users_list)
