from datetime import datetime
from enum import Enum
from typing import List

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class AvailabilityStatus(Enum):
    """
    An enum representing available status options such as AVAILABLE, BUSY, and OFFLINE.
    """

    AVAILABLE: str = AVAILABLE  # TODO(autogpt): F821 Undefined name `AVAILABLE`
    BUSY: str = BUSY  # TODO(autogpt): F821 Undefined name `BUSY`
    OFFLINE: str = OFFLINE  # TODO(autogpt): F821 Undefined name `OFFLINE`


class Booking(BaseModel):
    """
    Details of a booking instance affecting professional availability.
    """

    id: str
    scheduledTime: datetime
    endTime: datetime
    status: prisma.enums.BookingStatus


class Availability(BaseModel):
    """
    Sub-model for the time slots of availability marked by the professional.
    """

    status: AvailabilityStatus
    timestamp: datetime


class SyncProfessionalAvailabilityResponse(BaseModel):
    """
    Provides confirmation and details related to updates in professional availability.
    """

    success: bool
    updatedAvailability: Availability


async def syncAvailability(
    professionalId: str, availabilityStatus: AvailabilityStatus, bookings: List[Booking]
) -> SyncProfessionalAvailabilityResponse:
    """
    Receives updates from the Booking System to adjust the availability of professionals in real-time based on changes in their schedules.

    Args:
        professionalId (str): The unique identifier for the professional whose availability is being updated.
        availabilityStatus (AvailabilityStatus): The current availability status of the professional.
        bookings (List[Booking]): A list of bookings that are influencing the professional's current availability.

    Returns:
        SyncProfessionalAvailabilityResponse: Provides confirmation and details related to updates in professional availability.
    """
    current_time = datetime.now()
    latest_availability = await prisma.models.Availability.prisma().find_first(
        where={"professionalId": professionalId}, order={"timestamp": "desc"}
    )
    is_busy = any(
        (
            booking.status == "CONFIRMED"
            and booking.scheduledTime
            <= current_time
            <= (booking.endTime or current_time)
            for booking in bookings
        )
    )
    new_status = AvailabilityStatus.BUSY if is_busy else availabilityStatus
    if latest_availability and latest_availability.status == new_status:
        updated_availability = latest_availability
    else:
        updated_availability = await prisma.models.Availability.prisma().upsert(
            where={"professionalId": professionalId},
            create={
                "professionalId": professionalId,
                "status": new_status,
                "timestamp": current_time,
            },
            update={"status": new_status, "timestamp": current_time},
        )  # TODO(autogpt): Argument missing for parameter "data". reportCallIssue
    return SyncProfessionalAvailabilityResponse(
        success=True,
        updatedAvailability=Availability(
            status=updated_availability.status, timestamp=updated_availability.timestamp
        ),
    )
