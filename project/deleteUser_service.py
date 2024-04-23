import prisma
import prisma.models
from pydantic import BaseModel


class DeleteUserResponse(BaseModel):
    """
    Response model indicating the successful deletion of a user.
    """

    message: str
    deletedUserId: str


async def deleteUser(userId: str) -> DeleteUserResponse:
    """
    Deletes a specific user from the system. Used by administrators to manage the roster of active users,
    essential for maintaining an up-to-date user base and ensuring only relevant users have access.

    Args:
        userId (str): The unique identifier of the user to be deleted.

    Returns:
        DeleteUserResponse: Response model indicating the successful deletion of a user.
    """
    try:
        deleted_user = await prisma.models.User.prisma().delete(where={"id": userId})
        return DeleteUserResponse(
            message="User successfully deleted.", deletedUserId=deleted_user.id
        )
    except Exception as e:
        return DeleteUserResponse(
            message=f"Failed to delete user: {str(e)}", deletedUserId=userId
        )
