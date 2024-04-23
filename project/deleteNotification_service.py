import prisma
import prisma.models
from pydantic import BaseModel


class DeleteNotificationResponse(BaseModel):
    """
    Response model indicating the outcome of the delete operation, including any pertinent status messages or errors.
    """

    success: bool
    message: str


async def deleteNotification(notificationId: str) -> DeleteNotificationResponse:
    """
    Removes a notification from the system by its ID. Assumes only authorized roles are permitted to delete notifications.

    Args:
        notificationId (str): The unique identifier of the notification to be deleted.

    Returns:
        DeleteNotificationResponse: Response model indicating the outcome of the delete operation, including any pertinent status messages or errors.
    """
    deleted_notification = await prisma.models.Notification.prisma().delete(
        where={"id": notificationId}
    )
    if deleted_notification:
        return DeleteNotificationResponse(
            success=True, message="Notification deleted successfully."
        )
    else:
        return DeleteNotificationResponse(
            success=False, message="Failed to delete notification."
        )
