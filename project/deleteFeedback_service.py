import prisma
import prisma.models
from pydantic import BaseModel


class DeleteFeedbackResponse(BaseModel):
    """
    Response model for the delete operation of feedback. It will simply return a success status indicating the feedback has been successfully deleted or not, since actual feedback data is not necessary to return upon deletion.
    """

    success: bool
    message: str


async def deleteFeedback(feedbackId: str) -> DeleteFeedbackResponse:
    """
    Deletes a specific feedback entry. This action is restricted to admins to maintain control over feedback management. Protected route.

    Args:
        feedbackId (str): Unique identifier for the feedback entry to be deleted.

    Returns:
        DeleteFeedbackResponse: Response model for the delete operation of feedback. It will simply return a success status indicating the feedback has been successfully deleted or not, since actual feedback data is not necessary to return upon deletion.
    """
    feedback = await prisma.models.Feedback.prisma().find_unique(
        where={"id": feedbackId}
    )
    if feedback is None:
        return DeleteFeedbackResponse(success=False, message="Feedback not found.")
    try:
        await prisma.models.Feedback.prisma().delete(where={"id": feedbackId})
        return DeleteFeedbackResponse(
            success=True, message="Feedback successfully deleted."
        )
    except Exception as e:
        return DeleteFeedbackResponse(
            success=False, message=f"Failed to delete feedback: {str(e)}"
        )
