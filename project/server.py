import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

import prisma
import prisma.enums
import project.createBooking_service
import project.createFeedback_service
import project.createNotification_service
import project.createUser_service
import project.deleteBooking_service
import project.deleteExternalCalendarEvent_service
import project.deleteFeedback_service
import project.deleteNotification_service
import project.deleteUser_service
import project.getAllBookings_service
import project.getAvailability_service
import project.getBooking_service
import project.getExternalCalendarEvents_service
import project.getFeedback_service
import project.getNotificationById_service
import project.getNotifications_service
import project.getUser_service
import project.getUserDetails_service
import project.listFeedbackForProfessional_service
import project.listUsers_service
import project.syncAvailability_service
import project.syncEventToExternalCalendar_service
import project.syncScheduleToAvailabilityModule_service
import project.updateAvailability_service
import project.updateBooking_service
import project.updateExternalCalendarEvent_service
import project.updateFeedback_service
import project.updateNotification_service
import project.updateUser_service
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from prisma import Prisma

logger = logging.getLogger(__name__)

db_client = Prisma(auto_register=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_client.connect()
    yield
    await db_client.disconnect()


app = FastAPI(
    title="Availability Checker",
    lifespan=lifespan,
    description="Function that returns the real-time availability of professionals, updating based on current activity or schedule.",
)


@app.get(
    "/sync-schedule",
    response_model=project.syncScheduleToAvailabilityModule_service.SyncScheduleResponse,
)
async def api_get_syncScheduleToAvailabilityModule(
    request: project.syncScheduleToAvailabilityModule_service.SyncScheduleRequest,
) -> project.syncScheduleToAvailabilityModule_service.SyncScheduleResponse | Response:
    """
    Provides schedule data fetched from external calendars to the Real-time Availability Module to update the professional's real-time status. This is a scheduled sync operation, crucial for the Availability System's accuracy.
    """
    try:
        res = project.syncScheduleToAvailabilityModule_service.syncScheduleToAvailabilityModule(
            request
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/feedback", response_model=project.createFeedback_service.PostFeedbackResponse
)
async def api_post_createFeedback(
    userId: str, professionalId: str, comment: Optional[str], rating: int
) -> project.createFeedback_service.PostFeedbackResponse | Response:
    """
    Creates a new feedback entry. This route captures user feedback and ratings for a service. It's protected to ensure that only authenticated users can submit feedback.
    """
    try:
        res = await project.createFeedback_service.createFeedback(
            userId, professionalId, comment, rating
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get("/users", response_model=project.listUsers_service.UsersResponse)
async def api_get_listUsers(
    request: project.listUsers_service.GetUsersRequest,
) -> project.listUsers_service.UsersResponse | Response:
    """
    Retrieves a list of all user profiles. It allows the admin to view all system users, which is essential for management and oversight.
    """
    try:
        res = await project.listUsers_service.listUsers(request)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.delete(
    "/external-calendar/events/{eventId}",
    response_model=project.deleteExternalCalendarEvent_service.DeleteExternalEventResponse,
)
async def api_delete_deleteExternalCalendarEvent(
    eventId: str,
) -> project.deleteExternalCalendarEvent_service.DeleteExternalEventResponse | Response:
    """
    Deletes an event from an external calendar. It’s used when appointments are canceled or no longer needed to avoid schedule blocks in professionals' calendars.
    """
    try:
        res = await project.deleteExternalCalendarEvent_service.deleteExternalCalendarEvent(
            eventId
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.put(
    "/feedback/{feedbackId}",
    response_model=project.updateFeedback_service.UpdateFeedbackResponse,
)
async def api_put_updateFeedback(
    feedbackId: str, comment: str, rating: int, admin_remarks: str
) -> project.updateFeedback_service.UpdateFeedbackResponse | Response:
    """
    Updates a specific feedback entry. Only accessible by admins to correct any discrepancies or add admin remarks. Protected route.
    """
    try:
        res = await project.updateFeedback_service.updateFeedback(
            feedbackId, comment, rating, admin_remarks
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.delete(
    "/bookings/{bookingId}",
    response_model=project.deleteBooking_service.CancelBookingResponse,
)
async def api_delete_deleteBooking(
    bookingId: str,
) -> project.deleteBooking_service.CancelBookingResponse | Response:
    """
    Cancels a specific booking and frees up the professional’s schedule by updating the Real-time Availability Module accordingly.
    """
    try:
        res = await project.deleteBooking_service.deleteBooking(bookingId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.delete(
    "/notifications/{notificationId}",
    response_model=project.deleteNotification_service.DeleteNotificationResponse,
)
async def api_delete_deleteNotification(
    notificationId: str,
) -> project.deleteNotification_service.DeleteNotificationResponse | Response:
    """
    Removes a notification from the system. This might be used when a notification is no longer relevant or was created in error. Secured access ensures that only authorized roles can delete notifications.
    """
    try:
        res = await project.deleteNotification_service.deleteNotification(
            notificationId
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post("/users", response_model=project.createUser_service.CreateUserProfileResponse)
async def api_post_createUser(
    email: str, password: str, role: project.createUser_service.UserRole
) -> project.createUser_service.CreateUserProfileResponse | Response:
    """
    Creates a new user profile. Designed for admin roles to add new professionals or users to the system. This is necessary for setting up access to different modules and features based on role.
    """
    try:
        res = await project.createUser_service.createUser(email, password, role)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/notifications",
    response_model=project.getNotifications_service.NotificationsFetchResponse,
)
async def api_get_getNotifications(
    filter_by_user_id: Optional[str],
    filter_by_read_status: Optional[bool],
    page: Optional[int],
    page_size: Optional[int],
) -> project.getNotifications_service.NotificationsFetchResponse | Response:
    """
    Retrieves a list of all notifications. This can be used by administrators to monitor and manage the notifications sent out to users and professionals. It supports filtering and pagination to aid in handling large datasets.
    """
    try:
        res = await project.getNotifications_service.getNotifications(
            filter_by_user_id, filter_by_read_status, page, page_size
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/users/{userId}", response_model=project.getUser_service.FetchUserDetailResponse
)
async def api_get_getUser(
    userId: str,
) -> project.getUser_service.FetchUserDetailResponse | Response:
    """
    Retrieves detailed information about a specific user. This endpoint supports individual user management tasks such as role verification, permission adjustments, and data verification.
    """
    try:
        res = project.getUser_service.getUser(userId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/notifications",
    response_model=project.createNotification_service.NotificationCreationResponse,
)
async def api_post_createNotification(
    userId: str, professionalId: Optional[str], message: str, eventType: str
) -> project.createNotification_service.NotificationCreationResponse | Response:
    """
    Creates a notification entity which will store data about events, such as availability changes or booking updates, that need to be communicated to users or professionals. Once created, this notification can trigger corresponding alert mechanisms. This route uses data from the Real-time Availability Module and the Booking System Module to compose relevant content.
    """
    try:
        res = await project.createNotification_service.createNotification(
            userId, professionalId, message, eventType
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.put(
    "/notifications/{notificationId}",
    response_model=project.updateNotification_service.NotificationUpdateResponse,
)
async def api_put_updateNotification(
    notificationId: str, message: str, read: bool
) -> project.updateNotification_service.NotificationUpdateResponse | Response:
    """
    Updates the details of a specific notification. This might be necessary to correct or append information pertaining to an evolving situation like change in availability or booking modifications. The input should include fields that are allowed to be updated, such as status or message content.
    """
    try:
        res = await project.updateNotification_service.updateNotification(
            notificationId, message, read
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/external-calendar/events",
    response_model=project.getExternalCalendarEvents_service.ExternalCalendarEventsResponse,
)
async def api_get_getExternalCalendarEvents(
    authorization_token: str,
    calendar_id: str,
    start_time: Optional[datetime],
    end_time: Optional[datetime],
) -> project.getExternalCalendarEvents_service.ExternalCalendarEventsResponse | Response:
    """
    Fetches events from an external calendar based on authorization credentials provided. It parses the events to a standard format useful to our system. Expected to integrate with popular calendar APIs like Google Calendar.
    """
    try:
        res = project.getExternalCalendarEvents_service.getExternalCalendarEvents(
            authorization_token, calendar_id, start_time, end_time
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/bookings/{bookingId}",
    response_model=project.getBooking_service.GetBookingDetailsResponse,
)
async def api_get_getBooking(
    bookingId: str,
) -> project.getBooking_service.GetBookingDetailsResponse | Response:
    """
    Fetches details of a specific booking, including all involved parties and status. This is used to view the details or manage the booking further.
    """
    try:
        res = await project.getBooking_service.getBooking(bookingId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.delete(
    "/users/{userId}", response_model=project.deleteUser_service.DeleteUserResponse
)
async def api_delete_deleteUser(
    userId: str,
) -> project.deleteUser_service.DeleteUserResponse | Response:
    """
    Deletes a specific user from the system. Used by administrators to manage the roster of active users, essential for maintaining an up-to-date user base and ensuring only relevant users have access.
    """
    try:
        res = await project.deleteUser_service.deleteUser(userId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/feedback/{feedbackId}",
    response_model=project.getFeedback_service.FeedbackDetailsResponse,
)
async def api_get_getFeedback(
    feedbackId: str,
) -> project.getFeedback_service.FeedbackDetailsResponse | Response:
    """
    Retrieves specific feedback details using the feedback ID. This is a protected route to ensure that feedback details are only accessible to authorized roles.
    """
    try:
        res = await project.getFeedback_service.getFeedback(feedbackId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.put(
    "/external-calendar/events/{eventId}",
    response_model=project.updateExternalCalendarEvent_service.UpdateEventResponse,
)
async def api_put_updateExternalCalendarEvent(
    eventId: str,
    startDateTime: datetime,
    endDateTime: Optional[datetime],
    title: str,
    description: Optional[str],
) -> project.updateExternalCalendarEvent_service.UpdateEventResponse | Response:
    """
    Updates specific event details in an external calendar. This is crucial for handling event changes like postponements or cancellations.
    """
    try:
        res = await project.updateExternalCalendarEvent_service.updateExternalCalendarEvent(
            eventId, startDateTime, endDateTime, title, description
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.put(
    "/users/{userId}",
    response_model=project.updateUser_service.UpdateUserDetailsResponse,
)
async def api_put_updateUser(
    userId: str, username: Optional[str], password: Optional[str]
) -> project.updateUser_service.UpdateUserDetailsResponse | Response:
    """
    Updates a user's details. Administrators can change roles, statuses, or other pertinent user information as necessary through this endpoint.
    """
    try:
        res = await project.updateUser_service.updateUser(userId, username, password)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.delete(
    "/feedback/{feedbackId}",
    response_model=project.deleteFeedback_service.DeleteFeedbackResponse,
)
async def api_delete_deleteFeedback(
    feedbackId: str,
) -> project.deleteFeedback_service.DeleteFeedbackResponse | Response:
    """
    Deletes a specific feedback entry. This action is restricted to admins to maintain control over feedback management. Protected route.
    """
    try:
        res = await project.deleteFeedback_service.deleteFeedback(feedbackId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/notifications/{notificationId}",
    response_model=project.getNotificationById_service.NotificationResponse,
)
async def api_get_getNotificationById(
    notificationId: str,
) -> project.getNotificationById_service.NotificationResponse | Response:
    """
    Fetches a single notification by its ID. This is useful for debugging or detailed tracking of specific notifications. It helps in understanding the contents and status of a single notification
    """
    try:
        res = await project.getNotificationById_service.getNotificationById(
            notificationId
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/feedback/professional/{professionalId}",
    response_model=project.listFeedbackForProfessional_service.FeedbackResponse,
)
async def api_get_listFeedbackForProfessional(
    professionalId: str,
) -> project.listFeedbackForProfessional_service.FeedbackResponse | Response:
    """
    Lists all feedback for a specific professional. This can be used by the Real-time Availability Module to fetch and display ratings, helping users choose top-rated professionals. Publicly accessible.
    """
    try:
        res = await project.listFeedbackForProfessional_service.listFeedbackForProfessional(
            professionalId
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/users/{userId}", response_model=project.getUserDetails_service.UserDetailsResponse
)
async def api_get_getUserDetails(
    userId: str,
) -> project.getUserDetails_service.UserDetailsResponse | Response:
    """
    Fetches detailed information of a specific user by user ID. It returns data such as username, user role, and activity status. The User Database Module is queried to retrieve this data.
    """
    try:
        res = await project.getUserDetails_service.getUserDetails(userId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get("/bookings", response_model=project.getAllBookings_service.GetBookingsOutput)
async def api_get_getAllBookings(
    date: Optional[str], professionalId: Optional[str], userId: Optional[str]
) -> project.getAllBookings_service.GetBookingsOutput | Response:
    """
    Retrieves a list of all bookings. Filters can be applied to sort by date, professional, or user.
    """
    try:
        res = await project.getAllBookings_service.getAllBookings(
            date, professionalId, userId
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/external-calendar/events",
    response_model=project.syncEventToExternalCalendar_service.ExternalCalendarEventSyncResponse,
)
async def api_post_syncEventToExternalCalendar(
    professionalId: str,
    calendarId: str,
    bookingDetails: project.syncEventToExternalCalendar_service.BookingDetails,
    apiKey: str,
) -> project.syncEventToExternalCalendar_service.ExternalCalendarEventSyncResponse | Response:
    """
    Sends local booking details to an external calendar, updating or creating new events based on availability and schedules to ensure calendars remain in sync. Works with multiple calendar APIs for broader accessibility.
    """
    try:
        res = await project.syncEventToExternalCalendar_service.syncEventToExternalCalendar(
            professionalId, calendarId, bookingDetails, apiKey
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/availability/update",
    response_model=project.updateAvailability_service.UpdateAvailabilityResponse,
)
async def api_post_updateAvailability(
    professionalId: str, status: project.updateAvailability_service.AvailabilityStatus
) -> project.updateAvailability_service.UpdateAvailabilityResponse | Response:
    """
    Updates availability status manually for a professional. This might be used by professionals or admins to set availability outside of standard hours or to override system-generated status based on calendar or bookings data.
    """
    try:
        res = await project.updateAvailability_service.updateAvailability(
            professionalId, status
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.put(
    "/bookings/{bookingId}",
    response_model=project.updateBooking_service.UpdateBookingResponse,
)
async def api_put_updateBooking(
    bookingId: str,
    scheduledTime: datetime,
    endTime: Optional[datetime],
    status: prisma.enums.BookingStatus,
    comments: Optional[str],
) -> project.updateBooking_service.UpdateBookingResponse | Response:
    """
    Updates a specific booking's details, such as rescheduling time or modifying services. Triggers an update to the Real-time Availability Module if there are changes affecting the schedule.
    """
    try:
        res = await project.updateBooking_service.updateBooking(
            bookingId, scheduledTime, endTime, status, comments
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/availability", response_model=project.getAvailability_service.AvailabilityResponse
)
async def api_get_getAvailability(
    professionalId: Optional[str], dateRange: Optional[str]
) -> project.getAvailability_service.AvailabilityResponse | Response:
    """
    Fetches real-time availability of professionals. It combines data from the Calendar Integration Module to consider schedules and interacts with the Booking System Module to account for recent bookings, ensuring the availability data reflects the latest changes.
    """
    try:
        res = await project.getAvailability_service.getAvailability(
            professionalId, dateRange
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/availability-sync",
    response_model=project.syncAvailability_service.SyncProfessionalAvailabilityResponse,
)
async def api_post_syncAvailability(
    professionalId: str,
    availabilityStatus: project.syncAvailability_service.AvailabilityStatus,
    bookings: List[project.syncAvailability_service.Booking],
) -> project.syncAvailability_service.SyncProfessionalAvailabilityResponse | Response:
    """
    Receives updates from the Booking System to adjust the availability of professionals in real-time based on changes in their schedules.
    """
    try:
        res = await project.syncAvailability_service.syncAvailability(
            professionalId, availabilityStatus, bookings
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/bookings", response_model=project.createBooking_service.CreateBookingResponse
)
async def api_post_createBooking(
    professionalId: str,
    userId: str,
    scheduledTime: datetime,
    endTime: datetime,
    serviceType: str,
) -> project.createBooking_service.CreateBookingResponse | Response:
    """
    Creates a new booking. It details the appointment time, professional involved, and service type. On success, it sends an update to the Real-time Availability Module to adjust the professional's availability.
    """
    try:
        res = await project.createBooking_service.createBooking(
            professionalId, userId, scheduledTime, endTime, serviceType
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )
