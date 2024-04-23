from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class NotificationCreationResponse(BaseModel):
    """
    Response model confirming the creation of the notification and providing basic info about the created entity.
    """

    success: bool
    notificationId: str
    message: str


async def createNotification(
    userId: str, professionalId: Optional[str], message: str, eventType: str
) -> NotificationCreationResponse:
    """
    Creates a notification entity which will store data about events, such as availability changes or booking updates, that need to be communicated to users or professionals. Once created, this notification can trigger corresponding alert mechanisms. This route uses data from the Real-time Availability Module and the Booking System Module to compose relevant content.

    Args:
        userId (str): The identifier for the user who will receive the notification.
        professionalId (Optional[str]): The identifier for the professional relative to the notification. This is optional as not all notifications might directly involve a professional.
        message (str): The message content of the notification.
        eventType (str): The type of event that triggers the notification, e.g., 'availability_change' or 'booking_update'.

    Returns:
        NotificationCreationResponse: Response model confirming the creation of the notification and providing basic info about the created entity.
    """
    notification = await prisma.models.Notification.prisma().create(
        data={"userId": userId, "message": message}
    )
    return NotificationCreationResponse(
        success=True, notificationId=notification.id, message=message
    )
