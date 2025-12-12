# test_google_calendar.py
from mcp_calendar_server import get_google_service
from datetime import datetime, timedelta

svc_tuple, err = get_google_service()
if err:
    print("Error:", err)
    raise SystemExit

service, calendar_id = svc_tuple
now = datetime.utcnow().isoformat() + "Z"
tomorrow = (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z"

events_result = service.events().list(
    calendarId=calendar_id,
    timeMin=now,
    timeMax=tomorrow,
    maxResults=5,
    singleEvents=True,
    orderBy="startTime",
).execute()

print("Found events:")
for item in events_result.get("items", []):
    print("-", item.get("summary"), item.get("start"))

