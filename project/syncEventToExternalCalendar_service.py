from datetime import datetime
from typing import Optional

import httpx
from pydantic import BaseModel


class BookingDetails(BaseModel):
    """
    Detailed model for the booking, which includes essential timing and participant information.
    """

    bookingId: str
    scheduledTime: datetime
    endTime: datetime
    title: str


class ExternalCalendarEventSyncResponse(BaseModel):
    """
    Response model indicating the success or failure of the sync operation, including any relevant messages or identifiers from the external calendar.
    """

    success: bool
    message: str
    externalEventId: Optional[str] = None


async def syncEventToExternalCalendar(
    professionalId: str, calendarId: str, bookingDetails: BookingDetails, apiKey: str
) -> ExternalCalendarEventSyncResponse:
    """
    Sends local booking details to an external calendar, updating or creating new events based on availability and schedules to ensure calendars remain in sync. Works with multiple calendar APIs for broader accessibility.

    Args:
        professionalId (str): The identifier for the professional whose bookings need to be synchronized.
        calendarId (str): The identifier for the specific external calendar where the event will be registered or updated.
        bookingDetails (BookingDetails): Details of the booking to be synced with the external calendar.
        apiKey (str): API key for authentication with the external calendar service.

    Returns:
        ExternalCalendarEventSyncResponse: Response model indicating the success or failure of the sync operation, including any relevant messages or identifiers from the external calendar.
    """
    url = f"https://api.externalcalendar.com/v1/calendars/{calendarId}/events"
    event_data = {
        "professionalId": professionalId,
        "title": bookingDetails.title,
        "start": bookingDetails.scheduledTime.isoformat(),
        "end": bookingDetails.endTime.isoformat(),
        "metadata": {"bookingId": bookingDetails.bookingId},
    }
    headers = {"Authorization": f"Bearer {apiKey}", "Content-Type": "application/json"}
    try:
        response = httpx.post(url, json=event_data, headers=headers)
        if response.status_code == 201:
            response_data = response.json()
            return ExternalCalendarEventSyncResponse(
                success=True,
                message="Booking successfully synced with external calendar.",
                externalEventId=response_data.get("id"),
            )
        else:
            return ExternalCalendarEventSyncResponse(
                success=False, message=f"Failed to sync booking: {response.text}"
            )
    except httpx.RequestError as http_error:
        return ExternalCalendarEventSyncResponse(
            success=False, message=f"HTTP request failed: {str(http_error)}"
        )
