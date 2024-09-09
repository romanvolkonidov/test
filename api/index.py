from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
import logging
import requests
from icalendar import Calendar
import pytz
from collections import defaultdict

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define the calendars to fetch events from
CALENDARS = [
    'https://calendar.google.com/calendar/ical/romanvolkonidov%40gmail.com/private-1b2dd71a5440e4cd42c7c7d4d77fd554/basic.ics',
    'https://calendar.google.com/calendar/ical/violetta6520%40gmail.com/private-4668f11232a35223fb2b7f0224414ac9/basic.ics',
    'https://calendar.google.com/calendar/ical/violetta6520%40gmail.com/public/basic.ics',
    'https://calendar.google.com/calendar/ical/p8simije0nhss305jf5qak5sm0%40group.calendar.google.com/private-8471e32b9a066146ba0545efc6d5322d/basic.ics',
    'https://calendar.google.com/calendar/ical/o6bemnc7uc56hipv6t6lntccq4%40group.calendar.google.com/private-1f621ee25080da2111e7f1c5598322a9/basic.ics'
]

# Nairobi time zone
NAIROBI_TZ = pytz.timezone('Africa/Nairobi')

# Function to fetch events from a single calendar
def fetch_events_from_calendar(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        calendar = Calendar.from_ical(response.text)
        events = []
        for component in calendar.walk():
            if component.name == "VEVENT":
                event = {
                    'summary': str(component.get('summary')),
                    'start': component.get('dtstart').dt.isoformat(),
                    'end': component.get('dtend').dt.isoformat()
                }
                events.append(event)
        return events
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching events from {url}: {e}")
        return []

# Function to filter events for today in Africa/Nairobi Time
def filter_events_for_today(events):
    today = datetime.now(NAIROBI_TZ).date()
    filtered_events = []
    for event in events:
        event_start = datetime.fromisoformat(event['start']).astimezone(NAIROBI_TZ).date()
        if event_start == today:
            event['local_start'] = datetime.fromisoformat(event['start']).astimezone(NAIROBI_TZ).strftime('%Y-%m-%d %H:%M:%S')
            event['local_end'] = datetime.fromisoformat(event['end']).astimezone(NAIROBI_TZ).strftime('%Y-%m-%d %H:%M:%S')
            filtered_events.append(event)
    return filtered_events

# Function to group events by summary
def group_events_by_summary(events):
    grouped_events = defaultdict(list)
    for event in events:
        grouped_events[event['summary']].append(event)
    return grouped_events

@app.route('/events', methods=['GET'])
def get_events():
    all_events = []
    for calendar_url in CALENDARS:
        events = fetch_events_from_calendar(calendar_url)
        all_events.extend(events)
    
    today_events = filter_events_for_today(all_events)
    grouped_events = group_events_by_summary(today_events)
    return jsonify(grouped_events)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
