from datetime import datetime

import prisma
import prisma.models
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    """
    Response model for the GET request to fetch notification details. It returns all relevant information about a particular notification as described in the Notification database model.
    """

    id: str
    userId: str
    message: str
    read: bool
    createdAt: datetime


async def getNotificationById(notificationId: str) -> NotificationResponse:
    """
    Fetches a single notification by its ID. This is useful for debugging or detailed tracking of specific notifications. It helps in understanding the contents and status of a single notification.

    Args:
        notificationId (str): The unique identifier for the notification to be retrieved.

    Returns:
        NotificationResponse: Response model for the GET request to fetch notification details. It returns all relevant information about a particular notification as described in the Notification database model.

    Example:
        notificationId = "abc123"
        notification = await getNotificationById(notificationId)
        > NotificationResponse(id="abc123", userId="user789", message="Reminder: Appointment Tomorrow", read=False, createdAt=datetime(2023, 3, 29, 12, 00))
    """
    notification_data = await prisma.models.Notification.prisma().find_unique(
        where={"id": notificationId}
    )
    if notification_data is None:
        raise ValueError("No notification found with the given ID.")
    return NotificationResponse(
        id=notification_data.id,
        userId=notification_data.userId,
        message=notification_data.message,
        read=notification_data.read,
        createdAt=notification_data.createdAt,
    )
