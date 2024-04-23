from datetime import datetime
from enum import Enum
from typing import List, Optional

import prisma
import prisma.models
from pydantic import BaseModel


class AvailabilityStatus(Enum):
    """
    An enum representing available status options such as AVAILABLE, BUSY, and OFFLINE.
    """

    AVAILABLE: str = AVAILABLE  # TODO(autogpt): F821 Undefined name `AVAILABLE`
    BUSY: str = BUSY  # TODO(autogpt): F821 Undefined name `BUSY`
    OFFLINE: str = OFFLINE  # TODO(autogpt): F821 Undefined name `OFFLINE`


class ProfessionalAvailability(BaseModel):
    """
    A detailed object containing availability information for a specific professional.
    """

    professionalId: str
    isAvailable: bool
    currentStatus: AvailabilityStatus
    nextAvailableTime: Optional[datetime] = None


class AvailabilityResponse(BaseModel):
    """
    Response model for providing the real-time availability status of professionals. This model will aggregate data from multiple sources to provide a comprehensive view of the professional's availability.
    """

    availabilities: List[ProfessionalAvailability]


async def getAvailability(
    professionalId: Optional[str], dateRange: Optional[str]
) -> AvailabilityResponse:
    """
    Fetches real-time availability of professionals. It combines data from the Calendar Integration Module to consider schedules and interacts with the Booking System Module to account for recent bookings, ensuring the availability data reflects the latest changes.

    Args:
        professionalId (Optional[str]): Optional parameter to filter availability by a specific professional's ID.
        dateRange (Optional[str]): Optional parameter to filter availability within a specific date range.

    Returns:
        AvailabilityResponse: Response model for providing the real-time availability status of professionals.

    Example:
        getAvailability(None, '2023-05-01/2023-05-15')
        > AvailabilityResponse(availabilities=[ProfessionalAvailability(...)])
    """
    if dateRange:
        start_date, end_date = dateRange.split("/")
        start_datetime = datetime.fromisoformat(start_date + "T00:00:00")
        end_datetime = datetime.fromisoformat(end_date + "T23:59:59")
    else:
        start_datetime = datetime.min
        end_datetime = datetime.max
    query = {"timestamp": {"gte": start_datetime, "lte": end_datetime}}
    if professionalId:
        query["professionalId"] = professionalId
    raw_availabilities = await prisma.models.Availability.prisma().find_many(
        where=query, include={"Professional": True}, order={"timestamp": "desc"}
    )
    professionals_availability = {}
    for availability in raw_availabilities:
        prof_id = availability.professionalId
        if prof_id not in professionals_availability:
            professionals_availability[prof_id] = ProfessionalAvailability(
                professionalId=prof_id,
                isAvailable=availability.Professional.isAvailable,
                currentStatus=AvailabilityStatus[availability.status.name],
                nextAvailableTime=availability.timestamp
                if availability.status != AvailabilityStatus.AVAILABLE
                else None,
            )
    response = AvailabilityResponse(
        availabilities=list(professionals_availability.values())
    )
    return response
