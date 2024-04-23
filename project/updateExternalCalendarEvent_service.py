from datetime import datetime
from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class UpdatedEvent(BaseModel):
    """
    Represents the updated state of the event after successful modification.
    """

    eventId: str
    startDateTime: datetime
    endDateTime: Optional[datetime] = None
    title: str
    description: Optional[str] = None


class UpdateEventResponse(BaseModel):
    """
    This model returns the result of the attempt to update an event in the external calendar. It provides confirmation of the update or details of any synchronization issues.
    """

    success: bool
    message: str
    updatedEvent: UpdatedEvent


async def updateExternalCalendarEvent(
    eventId: str,
    startDateTime: datetime,
    endDateTime: Optional[datetime],
    title: str,
    description: Optional[str],
) -> UpdateEventResponse:
    """
    Updates specific event details in an external calendar. This is crucial for handling event changes like postponements or cancellations.

    Args:
        eventId (str): The unique identifier for the event to be updated.
        startDateTime (datetime): The new start date and time for the event.
        endDateTime (Optional[datetime]): The new end date and time for the event, which can be null if the event is ongoing.
        title (str): The updated title of the event.
        description (Optional[str]): The updated description of the event, detailing the nature or purpose of the event.

    Returns:
        UpdateEventResponse: This model returns the result of the attempt to update an event in the external calendar. It provides confirmation of the update or details of any synchronization issues.
    """
    event = await prisma.models.CalendarEntry.prisma().find_unique(
        where={"id": eventId}
    )
    if event is None:
        return UpdateEventResponse(
            success=False, message="Event not found.", updatedEvent=None
        )
    updated_event = await prisma.models.CalendarEntry.prisma().update(
        where={"id": eventId},
        data={
            "startDateTime": startDateTime,
            "endDateTime": endDateTime,
            "title": title,
            "description": description,
        },
    )
    if updated_event:
        updated_event_details = UpdatedEvent(
            eventId=updated_event.id,
            startDateTime=updated_event.startDateTime,
            endDateTime=updated_event.endDateTime,
            title=updated_event.title,
            description=updated_event.description,
        )
        return UpdateEventResponse(
            success=True,
            message="Event updated successfully.",
            updatedEvent=updated_event_details,
        )
    else:
        return UpdateEventResponse(
            success=False, message="Failed to update the event.", updatedEvent=None
        )
