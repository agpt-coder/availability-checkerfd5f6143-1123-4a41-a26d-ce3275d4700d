from datetime import datetime

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class CreateBookingResponse(BaseModel):
    """
    Response model returning the details of the newly created booking or an error message if the operation failed.
    """

    bookingId: str
    status: prisma.enums.BookingStatus
    message: str


async def updateProfessionalAvailability(professionalId: str):
    """
    Updates the availability status of the professional based on the current bookings and calendar entries.

    This function checks if there are any current or upcoming bookings or calendar entries that overlap with the current time.
    If there are overlapping bookings or entries, the professional's availability is marked as busy.
    Otherwise, it is marked as available.

    Args:
        professionalId (str): Unique identifier for the professional.

    Returns:
        None
    """
    now = datetime.now()
    current_bookings = await prisma.models.Booking.prisma().find_many(
        where={
            "professionalId": professionalId,
            "scheduledTime": {"lte": now},
            "endTime": {"gte": now},
            "status": {"in": ["PENDING", "CONFIRMED"]},
        }
    )
    current_entries = await prisma.models.CalendarEntry.prisma().find_many(
        where={
            "professionalId": professionalId,
            "startDateTime": {"lte": now},
            "endDateTime": {"gte": now},
        }
    )
    is_busy = len(current_bookings) > 0 or len(current_entries) > 0
    await prisma.models.Professional.prisma().update(
        where={"id": professionalId}, data={"isAvailable": not is_busy}
    )


async def createBooking(
    professionalId: str,
    userId: str,
    scheduledTime: datetime,
    endTime: datetime,
    serviceType: str,
) -> CreateBookingResponse:
    """
    Creates a new booking. It details the appointment time, professional involved, and service type. On success, it sends an update to the Real-time Availability Module to adjust the professional's availability.

    Args:
    professionalId (str): Unique identifier for the professional involved in the booking.
    userId (str): Unique identifier for the user who is making the booking.
    scheduledTime (datetime): The scheduled start time for the appointment.
    endTime (datetime): The scheduled end time for the appointment.
    serviceType (str): The type of service for which the booking is made.

    Returns:
    CreateBookingResponse: Response model returning the details of the newly created booking or an error message if the operation failed.
    """
    try:
        professional = await prisma.models.Professional.prisma().find_unique(
            where={"id": professionalId}, include={"Availabilities": True}
        )
        if not professional:
            return CreateBookingResponse(
                bookingId="",
                status=prisma.enums.BookingStatus.CANCELLED,
                message="Professional not found.",
            )
        overlapping_bookings = await prisma.models.Booking.prisma().find_many(
            where={
                "professionalId": professionalId,
                "scheduledTime": {"lte": scheduledTime},
                "endTime": {"gte": endTime},
                "status": prisma.enums.BookingStatus.CONFIRMED,
            }
        )
        if overlapping_bookings:
            return CreateBookingResponse(
                bookingId="",
                status=prisma.enums.BookingStatus.CANCELLED,
                message="Time slot is not available.",
            )
        new_booking = await prisma.models.Booking.prisma().create(
            {
                "professionalId": professionalId,
                "userId": userId,
                "scheduledTime": scheduledTime,
                "endTime": endTime,
                "status": prisma.enums.BookingStatus.PENDING,
            }
        )
        await updateProfessionalAvailability(professionalId)
        return CreateBookingResponse(
            bookingId=new_booking.id,
            status=prisma.enums.BookingStatus.PENDING,
            message="Booking created successfully.",
        )
    except Exception as e:
        return CreateBookingResponse(
            bookingId="", status=prisma.enums.BookingStatus.CANCELLED, message=str(e)
        )
