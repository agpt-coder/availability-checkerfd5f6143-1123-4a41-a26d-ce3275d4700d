from datetime import datetime

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class DeleteExternalEventResponse(BaseModel):
    """
    Confirms the deletion of the event from the external calendar.
    """

    success: bool
    message: str


async def deleteExternalCalendarEvent(eventId: str) -> DeleteExternalEventResponse:
    """
    Deletes an event from an external calendar. It’s used when appointments are canceled
    or no longer needed to avoid blocks in professionals' calendars.

    Args:
    eventId (str): The unique identifier of the event in the external calendar that needs to be deleted.

    Returns:
    DeleteExternalEventResponse: Confirms the deletion of the event from the external calendar.
    """
    try:
        event = await prisma.models.CalendarEntry.prisma().find_unique(
            where={"id": eventId}, include={"Professional": True}
        )
        if event is None:
            return DeleteExternalEventResponse(
                success=False, message="Event not found."
            )
        await prisma.models.CalendarEntry.prisma().delete(where={"id": eventId})
        if event.Professional:
            await prisma.models.Availability.prisma().create(
                data={
                    "professionalId": event.professionalId,
                    "status": prisma.enums.AvailabilityStatus.AVAILABLE,
                    "timestamp": datetime.now(),
                }
            )
        return DeleteExternalEventResponse(
            success=True, message="Event successfully deleted."
        )
    except Exception as error:
        return DeleteExternalEventResponse(
            success=False, message=f"Error deleting event: {str(error)}"
        )
