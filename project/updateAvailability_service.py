import datetime
from enum import Enum

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


class UpdateAvailabilityResponse(BaseModel):
    """
    Response model for updating availability. Provides feedback on the success of the operation.
    """

    successful: bool
    message: str
    updatedStatus: AvailabilityStatus


async def updateAvailability(
    professionalId: str, status: AvailabilityStatus
) -> UpdateAvailabilityResponse:
    """
    Updates availability status manually for a professional. This might be used by professionals or admins
    to set availability outside of standard hours or to override system-generated status based on calendar or
    bookings data.

    Args:
        professionalId (str): The ID of the professional whose availability status is being updated.
        status (AvailabilityStatus): The new availability status for the professional.

    Returns:
        UpdateAvailabilityResponse: Response model for updating availability. Provides feedback on the success
        of the operation.
    """
    try:
        professional = await prisma.models.Professional.prisma().find_unique(
            where={"id": professionalId}
        )
        if not professional:
            return UpdateAvailabilityResponse(
                successful=False,
                message="Professional not found.",
                updatedStatus=status,
            )
        await prisma.models.Availability.prisma().create(
            data={
                "professionalId": professionalId,
                "status": status,
                "timestamp": datetime.datetime.now(),
            }
        )
        return UpdateAvailabilityResponse(
            successful=True,
            message="Availability status updated successfully.",
            updatedStatus=status,
        )
    except Exception as e:
        return UpdateAvailabilityResponse(
            successful=False,
            message=f"Failed to update availability status: {str(e)}",
            updatedStatus=status,
        )
