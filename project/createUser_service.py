from datetime import datetime
from enum import Enum

import bcrypt
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


class CreateUserProfileResponse(BaseModel):
    """
    The response model that returns user information once registered successfully in the system.
    """

    id: str
    email: str
    role: UserRole
    createdAt: datetime


async def createUser(
    email: str, password: str, role: UserRole
) -> CreateUserProfileResponse:
    """
    Creates a new user profile. Designed for admin roles to add new professionals or users to the system. This is necessary for setting up access to different modules and features based on role.

    Args:
        email (str): Email address of the new user, which must be unique.
        password (str): Password for the new user, which will be hashed and stored securely.
        role (UserRole): Role assigned to the user, determining the access level and functionalities available. It can be one of ['ADMIN', 'PROFESSIONAL', 'END_USER'].

    Returns:
        CreateUserProfileResponse: The response model that returns user information once registered successfully in the system.

    Example:
        create_user_response = await createUser("newuser@example.com", "securepass123", UserRole.END_USER)
        > CreateUserProfileResponse(id='123-456-789', email='newuser@example.com', role=UserRole.END_USER, createdAt=datetime.now())
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    user = await prisma.models.User.prisma().create(
        data={
            "email": email,
            "password": hashed_password.decode("utf-8"),
            "role": role.value,
        }
    )
    return CreateUserProfileResponse(
        id=user.id, email=user.email, role=UserRole[user.role], createdAt=user.createdAt
    )
