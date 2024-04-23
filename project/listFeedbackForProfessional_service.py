from datetime import datetime
from typing import List, Optional

import prisma
import prisma.models
from pydantic import BaseModel


class FeedbackModel(BaseModel):
    """
    A model representing a feedback entry.
    """

    id: str
    comment: Optional[str] = None
    rating: int
    createdAt: datetime
    userId: str


class FeedbackResponse(BaseModel):
    """
    Response model containing a list of feedback entries related to a specific professional.
    """

    feedbacks: List[FeedbackModel]


async def listFeedbackForProfessional(professionalId: str) -> FeedbackResponse:
    """
    Lists all feedback for a specific professional. This can be used by the Real-time Availability Module to fetch and display ratings, helping users choose top-rated professionals. Publicly accessible.

    Args:
        professionalId (str): The ID of the professional to fetch feedback for.

    Returns:
        FeedbackResponse: Response model containing a list of feedback entries related to a specific professional.
    """
    feedback_entities = await prisma.models.Feedback.prisma().find_many(
        where={"professionalId": professionalId}, include={"User": True}
    )
    feedback_models = [
        FeedbackModel(
            id=feedback.id,
            comment=feedback.comment,
            rating=feedback.rating,
            createdAt=feedback.createdAt,
            userId=feedback.userId,
        )
        for feedback in feedback_entities
    ]
    return FeedbackResponse(feedbacks=feedback_models)
