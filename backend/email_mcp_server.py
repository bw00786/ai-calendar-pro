"""
MCP Calendar Server with AI Agent Tools
Provides calendar operations via Model Context Protocol
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json

app = FastAPI(title="MCP Calendar Server", version="1.0.0")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
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

class CreateEventRequest(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: str
    end_time: str
    location: Optional[str] = None
    attendees: List[str] = []
    color: str = "#3b82f6"

class UpdateEventRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[str] = None
    end_time: datetime = Field(
        ..., 
        example=(datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
    )
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    color: Optional[str] = None

class MCPToolRequest(BaseModel):
    tool: str
    parameters: Dict[str, Any]

# In-memory storage (replace with database in production)
events_db: Dict[str, Event] = {}

# Utility functions
def generate_event_id() -> str:
    from uuid import uuid4
    return str(uuid4())

def parse_datetime(dt_str: str) -> datetime:
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

# MCP Tool Definitions
MCP_TOOLS = {
    "calendar_create_event": {
        "name": "calendar_create_event",
        "description": "Create a new calendar event",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Event title"},
                "description": {"type": "string", "description": "Event description"},
                "start_time": {"type": "string", "description": "Start time in ISO format"},
                "end_time": {"type": "string", "description": "End time in ISO format"},
                "location": {"type": "string", "description": "Event location"},
                "attendees": {"type": "array", "items": {"type": "string"}, "description": "List of attendees"},
                "color": {"type": "string", "description": "Event color hex code"}
            },
            "required": ["title", "start_time", "end_time"]
        }
    },
    "calendar_get_events": {
        "name": "calendar_get_events",
        "description": "Get calendar events, optionally filtered by date range",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Start date filter (ISO format)"},
                "end_date": {"type": "string", "description": "End date filter (ISO format)"}
            }
        }
    },
    "calendar_update_event": {
        "name": "calendar_update_event",
        "description": "Update an existing calendar event",
        "input_schema": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "Event ID to update"},
                "title": {"type": "string", "description": "New event title"},
                "description": {"type": "string", "description": "New event description"},
                "start_time": {"type": "string", "description": "New start time"},
                "end_time": {"type": "string", "description": "New end time"},
                "location": {"type": "string", "description": "New location"},
                "attendees": {"type": "array", "items": {"type": "string"}},
                "color": {"type": "string", "description": "New color"}
            },
            "required": ["event_id"]
        }
    },
    "calendar_delete_event": {
        "name": "calendar_delete_event",
        "description": "Delete a calendar event",
        "input_schema": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "Event ID to delete"}
            },
            "required": ["event_id"]
        }
    },
    "calendar_get_today_events": {
        "name": "calendar_get_today_events",
        "description": "Get all events for today",
        "input_schema": {"type": "object", "properties": {}}
    }
}

# MCP Endpoints
@app.get("/mcp/tools")
async def list_tools():
    """List all available MCP tools"""
    return {"tools": list(MCP_TOOLS.values())}

@app.post("/mcp/call")
async def call_tool(request: MCPToolRequest):
    """Execute an MCP tool"""
    tool = request.tool
    params = request.parameters
    
    if tool == "calendar_create_event":
        return await create_event_tool(params)
    elif tool == "calendar_get_events":
        return await get_events_tool(params)
    elif tool == "calendar_update_event":
        return await update_event_tool(params)
    elif tool == "calendar_delete_event":
        return await delete_event_tool(params)
    elif tool == "calendar_get_today_events":
        return await get_today_events_tool()
    else:
        raise HTTPException(status_code=400, detail=f"Unknown tool: {tool}")

# Tool Implementations
async def create_event_tool(params: Dict[str, Any]):
    event_id = generate_event_id()
    event = Event(
        id=event_id,
        title=params["title"],
        description=params.get("description"),
        start_time=parse_datetime(params["start_time"]),
        end_time=parse_datetime(params["end_time"]),
        location=params.get("location"),
        attendees=params.get("attendees", []),
        color=params.get("color", "#3b82f6")
    )
    events_db[event_id] = event
    return {"success": True, "event": event.dict()}

async def get_events_tool(params: Dict[str, Any]):
    start_date = params.get("start_date")
    end_date = params.get("end_date")
    
    filtered_events = list(events_db.values())
    
    if start_date:
        start = parse_datetime(start_date)
        filtered_events = [e for e in filtered_events if e.start_time >= start]
    
    if end_date:
        end = parse_datetime(end_date)
        filtered_events = [e for e in filtered_events if e.end_time <= end]
    
    return {"events": [e.dict() for e in filtered_events]}

async def update_event_tool(params: Dict[str, Any]):
    event_id = params["event_id"]
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event = events_db[event_id]
    
    if "title" in params:
        event.title = params["title"]
    if "description" in params:
        event.description = params["description"]
    if "start_time" in params:
        event.start_time = parse_datetime(params["start_time"])
    if "end_time" in params:
        event.end_time = parse_datetime(params["end_time"])
    if "location" in params:
        event.location = params["location"]
    if "attendees" in params:
        event.attendees = params["attendees"]
    if "color" in params:
        event.color = params["color"]
    
    return {"success": True, "event": event.dict()}

async def delete_event_tool(params: Dict[str, Any]):
    event_id = params["event_id"]
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail="Event not found")
    
    del events_db[event_id]
    return {"success": True, "deleted_id": event_id}

async def get_today_events_tool():
    today = datetime.now().date()
    today_events = [
        e for e in events_db.values()
        if e.start_time.date() == today
    ]
    return {"events": [e.dict() for e in today_events]}

# REST API Endpoints (for direct frontend access)
@app.post("/events", response_model=Event)
async def create_event(request: CreateEventRequest):
    event_id = generate_event_id()
    event = Event(
        id=event_id,
        title=request.title,
        description=request.description,
        start_time=parse_datetime(request.start_time),
        end_time=parse_datetime(request.end_time),
        location=request.location,
        attendees=request.attendees,
        color=request.color
    )
    events_db[event_id] = event
    return event

@app.get("/events", response_model=List[Event])
async def get_events(start_date: Optional[str] = None, end_date: Optional[str] = None):
    filtered_events = list(events_db.values())
    
    if start_date:
        start = parse_datetime(start_date)
        filtered_events = [e for e in filtered_events if e.start_time >= start]
    
    if end_date:
        end = parse_datetime(end_date)
        filtered_events = [e for e in filtered_events if e.end_time <= end]
    
    return filtered_events

@app.get("/events/{event_id}", response_model=Event)
async def get_event(event_id: str):
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail="Event not found")
    return events_db[event_id]

@app.put("/events/{event_id}", response_model=Event)
async def update_event(event_id: str, request: UpdateEventRequest):
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
    
    return event

@app.delete("/events/{event_id}")
async def delete_event(event_id: str):
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail="Event not found")
    
    del events_db[event_id]
    return {"success": True, "deleted_id": event_id}

@app.get("/events/today/list", response_model=List[Event])
async def get_today_events():
    today = datetime.now().date()
    today_events = [
        e for e in events_db.values()
        if e.start_time.date() == today
    ]
    return sorted(today_events, key=lambda x: x.start_time)

@app.get("/")
async def root():
    return {
        "message": "MCP Calendar Server",
        "version": "1.0.0",
        "mcp_tools_endpoint": "/mcp/tools",
        "mcp_call_endpoint": "/mcp/call"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)