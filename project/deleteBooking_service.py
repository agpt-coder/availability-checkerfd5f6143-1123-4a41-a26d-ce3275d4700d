import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class CancelBookingResponse(BaseModel):
    """
    Response model for a cancelled booking. Confirms that the booking has been cancelled and whether the corresponding professional's schedule was updated successfully.
    """

    success: bool
    message: str


async def deleteBooking(bookingId: str) -> CancelBookingResponse:
    """
    Cancels a specific booking and frees up the professional’s schedule by updating the Real-time Availability Module accordingly.

    Args:
        bookingId (str): Unique identifier for the booking that needs to be cancelled.

    Returns:
        CancelBookingResponse: Response model for a cancelled booking. Confirms that the booking has been cancelled and whether the corresponding professional's schedule was updated successfully.
    """
    booking = await prisma.models.Booking.prisma().find_unique(where={"id": bookingId})
    if not booking:
        return CancelBookingResponse(success=False, message="Booking not found.")
    if booking.status == prisma.enums.BookingStatus.CANCELLED:
        return CancelBookingResponse(
            success=False, message="Booking already cancelled."
        )
    updated_booking = await prisma.models.Booking.prisma().update(
        where={"id": bookingId}, data={"status": prisma.enums.BookingStatus.CANCELLED}
    )
    update_result = await prisma.models.Availability.prisma().update_many(
        where={
            "professionalId": booking.professionalId,
            "timestamp": {
                "gte": booking.scheduledTime,
                "lte": booking.endTime or booking.scheduledTime,
            },
        },
        data={"status": prisma.enums.AvailabilityStatus.AVAILABLE},
    )
    if (
        update_result.count > 0
    ):  # TODO(autogpt): Cannot access member "count" for type "int"
        #     Member "count" is unknown. reportAttributeAccessIssue
        return CancelBookingResponse(
            success=True,
            message="Booking cancelled successfully and professional's schedule updated.",
        )
    else:
        return CancelBookingResponse(
            success=True,
            message="Booking status was updated to cancelled, but schedule update failed.",
        )
