from datetime import datetime
from typing import Optional

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class UpdateBookingResponse(BaseModel):
    """
    Response model encapsulating the state of the booking after it has been updated.
    """

    bookingId: str
    scheduledTime: datetime
    endTime: Optional[datetime] = None
    status: prisma.enums.BookingStatus
    comments: Optional[str] = None


async def updateBooking(
    bookingId: str,
    scheduledTime: datetime,
    endTime: Optional[datetime],
    status: prisma.enums.BookingStatus,
    comments: Optional[str],
) -> UpdateBookingResponse:
    """
    Updates a specific booking's details, such as rescheduling time or modifying services. Triggers an update to the Real-time Availability Module if there are changes affecting the schedule.

    Args:
        bookingId (str): Identifier for the booking to be updated.
        scheduledTime (datetime): New scheduled start time for the booking, if applicable.
        endTime (Optional[datetime]): New scheduled end time for the booking, if different from the existing one.
        status (prisma.enums.BookingStatus): Updated status of the booking, based on defined prisma.enums.BookingStatus enum values.
        comments (Optional[str]): Additional comments or instructions related to the booking update.

    Returns:
        UpdateBookingResponse: Response model encapsulating the state of the booking after it has been updated.
    """
    booking = await prisma.models.Booking.prisma().find_unique(where={"id": bookingId})
    if not booking:
        raise ValueError("Booking with provided ID does not exist")
    updated_booking = await prisma.models.Booking.prisma().update(
        where={"id": bookingId},
        data={"scheduledTime": scheduledTime, "endTime": endTime, "status": status},
    )
    return UpdateBookingResponse(
        bookingId=updated_booking.id,
        scheduledTime=updated_booking.scheduledTime,
        endTime=updated_booking.endTime,
        status=status,
        comments=comments,
    )
