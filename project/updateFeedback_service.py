from datetime import datetime
from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class Feedback(BaseModel):
    """
    Complete details of the feedback that includes id, comment, rating, associated professional and user information.
    """

    id: str
    comment: str
    rating: int
    professionalId: str
    userId: str
    createdAt: datetime
    updatedAt: datetime
    admin_remarks: Optional[str] = None


class UpdateFeedbackResponse(BaseModel):
    """
    Defines the structure of the response after updating a feedback entry. Includes a success message and details of the updated feedback.
    """

    message: str
    updated_feedback: Feedback


async def updateFeedback(
    feedbackId: str, comment: str, rating: int, admin_remarks: str
) -> UpdateFeedbackResponse:
    """
    Updates a specific feedback entry. Only accessible by admins to correct any discrepancies or add admin remarks. Protected route.

    Args:
        feedbackId (str): The unique identifier of the feedback entry to be updated.
        comment (str): Revised commentary or feedback provided by the admin for updating.
        rating (int): Updated rating associated with the feedback.
        admin_remarks (str): Remarks or notes added by the admin during the update of the feedback.

    Returns:
        UpdateFeedbackResponse: Defines the structure of the response after updating a feedback entry. Includes a success message and details of the updated feedback.
    """
    feedback = await prisma.models.Feedback.prisma().find_unique(
        where={"id": feedbackId}
    )
    if not feedback:
        return UpdateFeedbackResponse(
            message="Feedback not found.", updated_feedback=None
        )
    await prisma.models.Feedback.prisma().update(
        where={"id": feedbackId},
        data={
            "comment": comment,
            "rating": rating,
            "admin_remarks": admin_remarks,
            "updatedAt": datetime.now(),
        },
    )
    updated_feedback = await prisma.models.Feedback.prisma().find_unique(
        where={"id": feedbackId}
    )
    return UpdateFeedbackResponse(
        message="Feedback updated successfully.", updated_feedback=updated_feedback
    )
