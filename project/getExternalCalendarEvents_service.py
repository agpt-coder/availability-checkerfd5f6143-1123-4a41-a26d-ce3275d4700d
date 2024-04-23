from datetime import datetime
from typing import List, Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pydantic import BaseModel


class EventsModel(BaseModel):
    """
    Represents an event in the system's standard format, derived from external calendar data.
    """

    event_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    is_all_day: bool


class ExternalCalendarEventsResponse(BaseModel):
    """
    Standardized event data format as used internally after fetching and transforming data from an external calendar's API response.
    """

    events: List[EventsModel]


def getExternalCalendarEvents(
    authorization_token: str,
    calendar_id: str,
    start_time: Optional[datetime],
    end_time: Optional[datetime],
) -> ExternalCalendarEventsResponse:
    """
    Fetches events from an external calendar based on authorization credentials provided. It parses the events to a standard format useful to our system. Expected to integrate with popular calendar APIs like Google Calendar.

    Args:
        authorization_token (str): OAuth token or similar credentials needed to access the external calendar API.
        calendar_id (str): Identifies the specific calendar from which to fetch events, typically a user's email or a unique identifier if multiple calendars exist.
        start_time (Optional[datetime]): Optional start time filter for fetching events that begin after this time.
        end_time (Optional[datetime]): Optional end time filter for fetching events that end before this time.

    Returns:
        ExternalCalendarEventsResponse: Standardized event data format as used internally after fetching and transforming data from an external calendar's API response.
    """
    service = build(
        "calendar", "v3", credentials=Credentials(token=authorization_token)
    )
    time_min = start_time.isoformat() if start_time else "1970-01-01T00:00:00Z"
    time_max = end_time.isoformat() if end_time else "2038-01-19T03:14:07Z"
    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    items = events_result.get("items", [])
    formatted_events = []
    for item in items:
        start_dt = datetime.fromisoformat(item["start"]["dateTime"])
        end_dt = (
            datetime.fromisoformat(item["end"]["dateTime"])
            if "dateTime" in item["end"]
            else None
        )
        formatted_events.append(
            EventsModel(
                event_id=item["id"],
                title=item["summary"],
                description=item.get("description"),
                start_time=start_dt,
                end_time=end_dt,
                location=item.get("location"),
                is_all_day="date" in item["start"],
            )
        )
    return ExternalCalendarEventsResponse(events=formatted_events)
