from datetime import datetime
from typing import List, Optional

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


class NotificationsFetchResponse(BaseModel):
    """
    Encapsulates the retrieved list of notifications along with possible pagination details.
    """

    notifications: List[Notification]
    total_count: int
    current_page: int
    total_pages: int


async def getNotifications(
    filter_by_user_id: Optional[str],
    filter_by_read_status: Optional[bool],
    page: Optional[int],
    page_size: Optional[int],
) -> NotificationsFetchResponse:
    """
    Retrieves a list of all notifications. This can be used by administrators to monitor and manage the notifications sent out to users and professionals. It supports filtering and pagination to aid in handling large datasets.

    Args:
        filter_by_user_id (Optional[str]): Optional user ID for which notifications are being retrieved. Leaving this blank retrieves notifications for all users.
        filter_by_read_status (Optional[bool]): Optional filter to retrieve notifications based on their read status. Leaving this blank retrieves both read and unread notifications.
        page (Optional[int]): Specifies the pagination page number. Defaults to 1 if not provided.
        page_size (Optional[int]): Specifies the number of notifications per page. Defaults to 10 if not provided.

    Returns:
        NotificationsFetchResponse: Encapsulates the retrieved list of notifications along with possible pagination details.
    """
    if page is None:
        page = 1
    if page_size is None:
        page_size = 10
    query = {}
    if filter_by_user_id:
        query["userId"] = filter_by_user_id
    if filter_by_read_status is not None:
        query["read"] = filter_by_read_status
    offset = (page - 1) * page_size
    notifications = await prisma.models.Notification.prisma().find_many(
        where=query, skip=offset, take=page_size
    )
    total_count = await prisma.models.Notification.prisma().count(where=query)
    total_pages = (total_count + page_size - 1) // page_size
    notification_models = [
        Notification(
            id=n.id,
            userId=n.userId,
            message=n.message,
            read=n.read,
            createdAt=n.createdAt,
        )
        for n in notifications
    ]
    return NotificationsFetchResponse(
        notifications=notification_models,
        total_count=total_count,
        current_page=page,
        total_pages=total_pages,
    )
