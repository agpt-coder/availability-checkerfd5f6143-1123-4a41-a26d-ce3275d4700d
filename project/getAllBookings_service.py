from datetime import datetime, timedelta
from typing import List, Optional

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class Booking(BaseModel):
    """
    Details of a booking instance affecting professional availability.
    """

    id: str
    scheduledTime: datetime
    endTime: datetime
    status: prisma.enums.BookingStatus


class GetBookingsOutput(BaseModel):
    """
    The output structure providing a list of bookings, optionally filtered. Each booking will display essential details linked to that booking instance.
    """

    bookings: List[Booking]


async def getAllBookings(
    date: Optional[str], professionalId: Optional[str], userId: Optional[str]
) -> GetBookingsOutput:
    """
    Retrieves a list of all bookings. Filters can be applied to sort by date, professional, or user.

    Args:
        date (Optional[str]): The specific date to filter bookings by. Format should be YYYY-MM-DD, filtering bookings occurring on this date.
        professionalId (Optional[str]): The ID of a professional to filter bookings by. Only bookings related to this professional will be shown.
        userId (Optional[str]): The ID of a user to filter bookings by. Only bookings related to this user will be shown.

    Returns:
        GetBookingsOutput: The output structure providing a list of bookings, optionally filtered. Each booking will display essential details linked to that booking instance.
    """
    query_conditions = []
    if userId:
        query_conditions.append({"userId": userId})
    if professionalId:
        query_conditions.append({"professionalId": professionalId})
    if date:
        query_conditions.append(
            {
                "scheduledTime": {
                    "gte": datetime.strptime(date, "%Y-%m-%d"),
                    "lt": datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1),
                }
            }
        )
    bookings = await prisma.models.Booking.prisma().find_many(
        where={"AND": query_conditions}
    )
    booking_models = [Booking(**booking.dict()) for booking in bookings]
    return GetBookingsOutput(bookings=booking_models)
