from datetime import datetime
from typing import Any, Dict, Optional

import prisma
import prisma.models
from pydantic import BaseModel


class FeedbackDetailsResponse(BaseModel):
    """
    This model represents the feedback details retrieved from the database, including associated user and professional information.
    """

    id: str
    comment: Optional[str] = None
    rating: int
    professional: Dict[str, Any]
    userDetails: Dict[str, Any]
    createdAt: datetime


async def getFeedback(feedbackId: str) -> FeedbackDetailsResponse:
    """
    Retrieves specific feedback details using the feedback ID. This is a protected route to ensure that feedback details are only accessible to authorized roles.

    Args:
        feedbackId (str): The unique identifier for the feedback, used to fetch the specific feedback details.

    Returns:
        FeedbackDetailsResponse: This model represents the feedback details retrieved from the database, including associated user and professional information.

    Raises:
        ValueError: If the feedback is not found.
    """
    feedback = await prisma.models.Feedback.prisma().find_unique(
        where={"id": feedbackId}, include={"User": True, "Professional": True}
    )
    if feedback is None:
        raise ValueError(f"prisma.models.Feedback with ID {feedbackId} not found.")
    response = FeedbackDetailsResponse(
        id=feedback.id,
        comment=feedback.comment,
        rating=feedback.rating,
        professional={
            "id": feedback.Professional.id,
            "userId": feedback.Professional.userId,
            "isAvailable": feedback.Professional.isAvailable,
        },
        userDetails={
            "id": feedback.User.id,
            "email": feedback.User.email,
            "role": feedback.User.role,
        },
        createdAt=feedback.createdAt,
    )
    return response
