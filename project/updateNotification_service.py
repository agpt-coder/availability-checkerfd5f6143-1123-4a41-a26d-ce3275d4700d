from datetime import datetime

import prisma
import prisma.models
from pydantic import BaseModel


class Notification(BaseModel):
    """
    The model representing notifications with fields from the Notification table in the database.
    """

    id: str
    userId: str
    message: str
    read: bool
    createdAt: datetime


class NotificationUpdateResponse(BaseModel):
    """
    Provides feedback if the updated operations on the notification were successful, including returning the full notification details post-update.
    """

    success: bool
    notification: Notification


async def updateNotification(
    notificationId: str, message: str, read: bool
) -> NotificationUpdateResponse:
    """
    Updates the details of a specific notification. This might be necessary to correct or append
    information pertaining to an evolving situation like change in availability or booking modifications.
    The input should include fields that are allowed to be updated, such as status or message content.

    Args:
    notificationId (str): The unique identifier of the notification to be updated.
    message (str): The updated message content for the notification.
    read (bool): Indicator if the notification has been read.

    Returns:
    NotificationUpdateResponse: Provides feedback if the updated operations on the notification
    were successful, including returning the full notification details post-update.
    """
    existing_notification = await prisma.models.Notification.prisma().find_unique(
        where={"id": notificationId}
    )
    if not existing_notification:
        return NotificationUpdateResponse(success=False, notification=None)
    updated_notification = await prisma.models.Notification.prisma().update(
        where={"id": notificationId}, data={"message": message, "read": read}
    )
    notification_model = Notification(
        id=updated_notification.id,
        userId=updated_notification.userId,
        message=updated_notification.message,
        read=updated_notification.read,
        createdAt=updated_notification.createdAt,
    )
    return NotificationUpdateResponse(success=True, notification=notification_model)
