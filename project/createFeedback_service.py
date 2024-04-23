from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class PostFeedbackResponse(BaseModel):
    """
    Confirmation of the feedback submission, including a copy of the submitted data.
    """

    success: bool
    feedbackId: str
    message: str


async def createFeedback(
    userId: str, professionalId: str, comment: Optional[str], rating: int
) -> PostFeedbackResponse:
    """
    Creates a new feedback entry. This route captures user feedback and ratings for a service. It's protected to ensure
    that only authenticated users can submit feedback.

    Args:
        userId (str): The unique identifier for the user providing feedback.
        professionalId (str): The unique identifier for the professional to whom the feedback is directed.
        comment (Optional[str]): Optional textual feedback provided by the user.
        rating (int): A numeric rating provided by the user, where applicable.

    Returns:
        PostFeedbackResponse: Confirmation of the feedback submission, including a copy of the submitted data.
    """
    try:
        new_feedback = await prisma.models.Feedback.prisma().create(
            data={
                "userId": userId,
                "professionalId": professionalId,
                "comment": comment,
                "rating": rating,
            }
        )
        return PostFeedbackResponse(
            success=True,
            feedbackId=new_feedback.id,
            message="Feedback submitted successfully.",
        )
    except Exception as exc:
        return PostFeedbackResponse(success=False, feedbackId="", message=str(exc))
