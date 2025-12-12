"""
Enhanced MCP Calendar Server with Email Notifications & Google Calendar Sync
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

app = FastAPI(title="Enhanced MCP Calendar Server", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
SCOPES = ['https://www.googleapis.com/auth/calendar']
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")


# -------------------------------------------------------------------
# Data Models
# -------------------------------------------------------------------

class Event(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendees: List[str] = []
    color: str = "#3b82f6"
    created_at: datetime = Field(default_factory=datetime.now)
    reminder_sent: bool = False
    google_event_id: Optional[str] = None
    notify_attendees: bool = True


class CreateEventRequest(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: str
    end_time: str
    location: Optional[str] = None
    attendees: List[str] = []
    color: str = "#3b82f6"
    notify_attendees: bool = True
    sync_to_google: bool = False


class UpdateEventRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    color: Optional[str] = None
    notify_attendees: Optional[bool] = None


class EmailNotificationRequest(BaseModel):
    event_id: str
    recipient: EmailStr
    notification_type: str = "reminder"  # reminder, invitation, update, cancellation


class MCPToolRequest(BaseModel):
    tool: str
    parameters: Dict[str, Any]


# In-memory storage
events_db: Dict[str, Event] = {}

# Google Calendar Service
google_calendar_service = None


# -------------------------------------------------------------------
# Google Calendar Integration
# -------------------------------------------------------------------

def get_google_calendar_service():
    global google_calendar_service
    if google_calendar_service is not None:
        return google_calendar_service

    creds = None
    # Token file stores user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists('credentials.json'):
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES
                )
                creds = flow.run_local_server(port=0)

        # Save credentials for next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    google_calendar_service = build('calendar', 'v3', credentials=creds)
    return google_calendar_service


def sync_to_google_calendar(event: Event) -> str:
    """Sync event to Google Calendar"""
    try:
        service = get_google_calendar_service()

        google_event = {
            'summary': event.title,
            'location': event.location or '',
            'description': event.description or '',
            'start': {
                'dateTime': event.start_time.isoformat(),
                'timeZone': 'America/Chicago',
            },
            'end': {
                'dateTime': event.end_time.isoformat(),
                'timeZone': 'America/Chicago',
            },
            'attendees': [{'email': email} for email in event.attendees],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 30},
                ],
            },
        }

        if event.google_event_id:
            # Update existing event
            result = service.events().update(
                calendarId='primary',
                eventId=event.google_event_id,
                body=google_event,
            ).execute()
        else:
            # Create new event
            result = service.events().insert(
                calendarId='primary',
                body=google_event,
            ).execute()

        return result.get('id', '')
    except Exception as e:
        print(f"Google Calendar sync error: {str(e)}")
        return ""


def import_from_google_calendar(time_min: datetime, time_max: datetime) -> List[Event]:
    """Import events from Google Calendar within a time range"""
    try:
        service = get_google_calendar_service()

        events_result = (
            service.events()
            .list(
                calendarId='primary',
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime',
            )
            .execute()
        )

        events = events_result.get('items', [])
        imported_events = []

        for g_event in events:
            event_id = g_event.get('id', '')
            event = Event(
                id=event_id,
                title=g_event.get('summary', 'No Title'),
                description=g_event.get('description', ''),
                start_time=datetime.fromisoformat(
                    g_event['start'].get('dateTime', g_event['start'].get('date'))
                ),
                end_time=datetime.fromisoformat(
                    g_event['end'].get('dateTime', g_event['end'].get('date'))
                ),
                location=g_event.get('location', ''),
                attendees=[a['email'] for a in g_event.get('attendees', [])],
                google_event_id=g_event['id'],
            )
            events_db[event_id] = event
            imported_events.append(event)

        return imported_events
    except Exception as e:
        print(f"Google Calendar import error: {str(e)}")
        return []


# -------------------------------------------------------------------
# Email Notifications
# -------------------------------------------------------------------

def send_email_notification(event: Event, recipient: str, notification_type: str):
    """Send email notification for an event"""
    if not EMAIL_USER or not EMAIL_PASSWORD:
        print("Email credentials not configured")
        return False

    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_USER
        msg['To'] = recipient

        if notification_type == "reminder":
            msg['Subject'] = f"Reminder: {event.title}"
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <h2 style="color: #3b82f6;">Event Reminder</h2>
                    <p>This is a reminder for your upcoming event:</p>
                    <div style="background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 10px 0;">
                        <h3 style="margin: 0;">{event.title}</h3>
                        <p><strong>When:</strong> {event.start_time.strftime('%B %d, %Y at %I:%M %p')}</p>
                        <p><strong>Duration:</strong> {event.start_time.strftime('%I:%M %p')} - {event.end_time.strftime('%I:%M %p')}</p>
                        {f'<p><strong>Location:</strong> {event.location}</p>' if event.location else ''}
                    </div>
                    <p style="color: #6b7280; font-size: 12px;">Sent from AI Calendar</p>
                </body>
            </html>
            """
        elif notification_type == "invitation":
            msg['Subject'] = f"Invitation: {event.title}"
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <h2 style="color: #10b981;">You're Invited!</h2>
                    <p>You've been invited to the following event:</p>
                    <div style="background: #ecfdf5; padding: 15px; border-radius: 8px; margin: 10px 0;">
                        <h3 style="margin: 0;">{event.title}</h3>
                        <p><strong>When:</strong> {event.start_time.strftime('%B %d, %Y at %I:%M %p')}</p>
                        <p><strong>Duration:</strong> {event.start_time.strftime('%I:%M %p')} - {event.end_time.strftime('%I:%M %p')}</p>
                        {f'<p><strong>Location:</strong> {event.location}</p>' if event.location else ''}
                    </div>
                    <p style="color: #6b7280; font-size: 12px;">Sent from AI Calendar</p>
                </body>
            </html>
            """
        elif notification_type == "update":
            msg['Subject'] = f"Updated: {event.title}"
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <h2 style="color: #f59e0b;">Event Updated</h2>
                    <p>The following event has been updated:</p>
                    <div style="background: #fef9c3; padding: 15px; border-radius: 8px; margin: 10px 0;">
                        <h3 style="margin: 0;">{event.title}</h3>
                        <p><strong>When:</strong> {event.start_time.strftime('%B %d, %Y at %I:%M %p')}</p>
                        <p><strong>Duration:</strong> {event.start_time.strftime('%I:%M %p')} - {event.end_time.strftime('%I:%M %p')}</p>
                        {f'<p><strong>Location:</strong> {event.location}</p>' if event.location else ''}
                    </div>
                    <p style="color: #6b7280; font-size: 12px;">Sent from AI Calendar</p>
                </body>
            </html>
            """
        else:  # cancellation
            msg['Subject'] = f"Cancelled: {event.title}"
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <h2 style="color: #ef4444;">Event Cancelled</h2>
                    <p>The following event has been cancelled:</p>
                    <div style="background: #fee2e2; padding: 15px; border-radius: 8px; margin: 10px 0;">
                        <h3 style="margin: 0; color: #991b1b;">{event.title}</h3>
                        <p><strong>When:</strong> {event.start_time.strftime('%B %d, %Y at %I:%M %p')}</p>
                        {f'<p><strong>Location:</strong> {event.location}</p>' if event.location else ''}
                    </div>
                    <p style="color: #6b7280; font-size: 12px;">Sent from AI Calendar</p>
                </body>
            </html>
            """

        part = MIMEText(body, 'html')
        msg.attach(part)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, recipient, msg.as_string())
        server.quit()

        return True
    except Exception as e:
        print(f"Email sending error: {str(e)}")
        return False


# -------------------------------------------------------------------
# Utility
# -------------------------------------------------------------------

def generate_event_id() -> str:
    from uuid import uuid4
    return str(uuid4())


def parse_datetime(dt_str: str) -> datetime:
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except Exception:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")


# -------------------------------------------------------------------
# Enhanced MCP Tools metadata
# -------------------------------------------------------------------

MCP_TOOLS = {
    "calendar_create_event": {
        "name": "calendar_create_event",
        "description": "Create a new calendar event with optional Google Calendar sync and email notifications",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "start_time": {"type": "string"},
                "end_time": {"type": "string"},
                "location": {"type": "string"},
                "attendees": {"type": "array", "items": {"type": "string"}},
                "color": {"type": "string"},
                "notify_attendees": {"type": "boolean"},
                "sync_to_google": {"type": "boolean"},
            },
            "required": ["title", "start_time", "end_time"],
        },
    },
    "calendar_send_reminder": {
        "name": "calendar_send_reminder",
        "description": "Send email reminder for an event",
        "input_schema": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string"},
                "recipient": {"type": "string"},
            },
            "required": ["event_id", "recipient"],
        },
    },
    "calendar_sync_google": {
        "name": "calendar_sync_google",
        "description": "Sync an event to Google Calendar",
        "input_schema": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string"},
            },
            "required": ["event_id"],
        },
    },
    "calendar_import_google": {
        "name": "calendar_import_google",
        "description": "Import events from Google Calendar",
        "input_schema": {
            "type": "object",
            "properties": {
                "days_ahead": {"type": "integer", "description": "Number of days to import"},
            },
        },
    },
}


# -------------------------------------------------------------------
# MCP Tool Implementations
# -------------------------------------------------------------------

async def create_event_tool(params: Dict[str, Any], background_tasks: BackgroundTasks):
    event_id = generate_event_id()
    event = Event(
        id=event_id,
        title=params["title"],
        description=params.get("description"),
        start_time=parse_datetime(params["start_time"]),
        end_time=parse_datetime(params["end_time"]),
        location=params.get("location"),
        attendees=params.get("attendees", []),
        color=params.get("color", "#3b82f6"),
        notify_attendees=params.get("notify_attendees", True),
    )
    events_db[event_id] = event

    # Optionally sync to Google
    if params.get("sync_to_google"):
        google_event_id = sync_to_google_calendar(event)
        if google_event_id:
            event.google_event_id = google_event_id

    # Optionally send invitations
    if event.notify_attendees and event.attendees:
        for attendee in event.attendees:
            background_tasks.add_task(send_email_notification, event, attendee, "invitation")

    return {"success": True, "event": event.dict()}


async def send_reminder_tool(params: Dict[str, Any], background_tasks: BackgroundTasks):
    event_id = params["event_id"]
    recipient = params["recipient"]

    if event_id not in events_db:
        raise HTTPException(status_code=404, detail="Event not found")

    event = events_db[event_id]
    background_tasks.add_task(send_email_notification, event, recipient, "reminder")

    return {"success": True, "message": f"Reminder sent to {recipient}"}


async def sync_google_tool(params: Dict[str, Any]):
    """
    Sync an event to Google Calendar.

    Supports two calling styles:
    1) Via event_id of an already-created event:
       {"event_id": "<id>"}

    2) Direct details (no event_id):
       {
         "title": "Meeting",
         "start_time": "2025-12-12T13:00:00Z",
         "end_time": "2025-12-12T14:00:00Z",
         "description": "...",      # optional
         "location": "...",         # optional
         "attendees": [...],        # optional
         "color": "#3b82f6"         # optional
       }
       In this case we create a new Event on the fly, sync it, and store it.
    """

    event_id = params.get("event_id")

    # ---- Case 1: caller provided an event_id ----
    if event_id:
        if event_id not in events_db:
            raise HTTPException(status_code=404, detail="Event not found")

        event = events_db[event_id]
        google_event_id = sync_to_google_calendar(event)

        if google_event_id:
            event.google_event_id = google_event_id
            return {"success": True, "google_event_id": google_event_id}

        return {"success": False, "message": "Failed to sync with Google Calendar"}

    # ---- Case 2: caller passed raw details (like your current logs) ----
    start_time = params.get("start_time")
    end_time = params.get("end_time")
    title = params.get("title", "Untitled Event")

    if not start_time or not end_time:
        raise HTTPException(
            status_code=400,
            detail="calendar_sync_google expects either event_id "
                   "or start_time and end_time.",
        )

    temp_event = Event(
        id=generate_event_id(),
        title=title,
        description=params.get("description"),
        start_time=parse_datetime(start_time),
        end_time=parse_datetime(end_time),
        location=params.get("location"),
        attendees=params.get("attendees", []),
        color=params.get("color", "#3b82f6"),
    )

    google_event_id = sync_to_google_calendar(temp_event)

    if google_event_id:
        temp_event.google_event_id = google_event_id
        # Optionally store it so /events can see it later
        events_db[temp_event.id] = temp_event
        return {
            "success": True,
            "google_event_id": google_event_id,
            "event": temp_event.dict(),
        }

    return {"success": False, "message": "Failed to sync with Google Calendar"}



async def import_google_tool(params: Dict[str, Any]):
    days_ahead = params.get("days_ahead", 30)
    time_min = datetime.now()
    time_max = time_min + timedelta(days=days_ahead)

    imported_events = import_from_google_calendar(time_min, time_max)

    return {
        "success": True,
        "imported_count": len(imported_events),
        "events": [e.dict() for e in imported_events],
    }


# -------------------------------------------------------------------
# Enhanced Endpoints
# -------------------------------------------------------------------

@app.get("/mcp/tools")
async def list_tools():
    return {"tools": list(MCP_TOOLS.values())}


@app.post("/mcp/call")
async def call_tool(request: MCPToolRequest, background_tasks: BackgroundTasks):
    tool = request.tool
    params = request.parameters

    print("\n🟦 MCP SERVER RECEIVED:")
    print(f"  Tool: {tool}")
    print(f"  Parameters: {params}")

    if tool == "calendar_create_event":
        return await create_event_tool(params, background_tasks)
    elif tool == "calendar_send_reminder":
        return await send_reminder_tool(params, background_tasks)
    elif tool == "calendar_sync_google":
        return await sync_google_tool(params)
    elif tool == "calendar_import_google":
        return await import_google_tool(params)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown tool: {tool}")


@app.post("/events", response_model=Event)
async def create_event(request: CreateEventRequest, background_tasks: BackgroundTasks):
    event_id = generate_event_id()
    event = Event(
        id=event_id,
        title=request.title,
        description=request.description,
        start_time=parse_datetime(request.start_time),
        end_time=parse_datetime(request.end_time),
        location=request.location,
        attendees=request.attendees,
        color=request.color,
        notify_attendees=request.notify_attendees,
    )
    events_db[event_id] = event

    if request.sync_to_google:
        google_event_id = sync_to_google_calendar(event)
        if google_event_id:
            event.google_event_id = google_event_id

    if event.notify_attendees and event.attendees:
        for attendee in event.attendees:
            background_tasks.add_task(send_email_notification, event, attendee, "invitation")

    return event


@app.get("/events", response_model=List[Event])
async def list_events():
    return list(events_db.values())


@app.get("/events/{event_id}", response_model=Event)
async def get_event(event_id: str):
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail="Event not found")
    return events_db[event_id]


@app.put("/events/{event_id}", response_model=Event)
async def update_event(event_id: str, request: UpdateEventRequest, background_tasks: BackgroundTasks):
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail="Event not found")

    event = events_db[event_id]

    if request.title is not None:
        event.title = request.title
    if request.description is not None:
        event.description = request.description
    if request.start_time is not None:
        event.start_time = parse_datetime(request.start_time)
    if request.end_time is not None:
        event.end_time = parse_datetime(request.end_time)
    if request.location is not None:
        event.location = request.location
    if request.attendees is not None:
        event.attendees = request.attendees
    if request.color is not None:
        event.color = request.color
    if request.notify_attendees is not None:
        event.notify_attendees = request.notify_attendees

    # Send update emails if needed
    if event.notify_attendees and event.attendees:
        for attendee in event.attendees:
            background_tasks.add_task(send_email_notification, event, attendee, "update")

    return event


@app.delete("/events/{event_id}")
async def delete_event(event_id: str, background_tasks: BackgroundTasks):
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail="Event not found")

    event = events_db[event_id]

    # Send cancellation emails if needed
    if event.notify_attendees and event.attendees:
        for attendee in event.attendees:
            background_tasks.add_task(send_email_notification, event, attendee, "cancellation")

    del events_db[event_id]
    return {"success": True}


@app.post("/events/{event_id}/reminder")
async def send_event_reminder(event_id: str, request: EmailNotificationRequest, background_tasks: BackgroundTasks):
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail="Event not found")

    event = events_db[event_id]
    background_tasks.add_task(send_email_notification, event, request.recipient, request.notification_type)

    return {"success": True}


@app.post("/events/{event_id}/sync-google")
async def sync_event_to_google(event_id: str):
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail="Event not found")

    event = events_db[event_id]
    google_event_id = sync_to_google_calendar(event)

    if google_event_id:
        event.google_event_id = google_event_id
        return {"success": True, "google_event_id": google_event_id}

    return {"success": False, "message": "Failed to sync with Google Calendar"}


@app.get("/events/import-google")
async def import_google_events(days_ahead: int = 30):
    time_min = datetime.now()
    time_max = time_min + timedelta(days=days_ahead)

    imported_events = import_from_google_calendar(time_min, time_max)

    return {
        "success": True,
        "imported_count": len(imported_events),
        "events": [e.dict() for e in imported_events],
    }


@app.get("/")
async def root():
    return {
        "message": "Enhanced MCP Calendar Server",
        "version": "2.0.0",
        "features": ["Email Notifications", "Google Calendar Sync", "Voice Input Ready"],
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
