from datetime import datetime
from typing import Optional

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class UserDetails(BaseModel):
    """
    Details model for the user including name and contact information.
    """

    name: str
    email: str


class ProfessionalDetails(BaseModel):
    """
    Model containing professional's business information.
    """

    fullName: str
    contactNumber: str


class GetBookingDetailsResponse(BaseModel):
    """
    Provides the details of a booking, including information about the user, the professional involved, and the current status of the booking.
    """

    bookingId: str
    userId: str
    professionalId: str
    scheduledTime: datetime
    endTime: Optional[datetime] = None
    status: prisma.enums.BookingStatus
    userDetails: UserDetails
    professionalDetails: ProfessionalDetails


async def getBooking(bookingId: str) -> GetBookingDetailsResponse:
    """
    Fetches details of a specific booking, including all involved parties and status.
    This function is used to view the details or manage the booking further.

    Args:
        bookingId (str): The unique identifier for the booking we want to retrieve.

    Returns:
        GetBookingDetailsResponse: Provides the details of a booking, including information about the user,
                                   the professional involved, and the current status of the booking.
    """
    booking = await prisma.models.Booking.prisma().find_unique(
        where={"id": bookingId}, include={"User": True, "Professional": True}
    )
    if not booking:
        raise ValueError("Booking not found")
    user_details = UserDetails(
        name=booking.User.email.split("@")[0], email=booking.User.email
    )
    professional = await prisma.models.Professional.prisma().find_unique(
        where={"id": booking.professionalId}, include={"User": True}
    )
    professional_details = ProfessionalDetails(
        fullName=professional.User.email.split("@")[0],
        contactNumber="Contact Number Not Available",
    )
    get_booking_response = GetBookingDetailsResponse(
        bookingId=booking.id,
        userId=booking.userId,
        professionalId=booking.professionalId,
        scheduledTime=booking.scheduledTime,
        endTime=booking.endTime,
        status=booking.status,
        userDetails=user_details,
        professionalDetails=professional_details,
    )
    return get_booking_response
