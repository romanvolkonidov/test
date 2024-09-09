from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime
import logging
import requests
from icalendar import Calendar, Event
import pytz

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Your iCal URL
ICAL_URL = 'https://calendar.google.com/calendar/ical/romanvolkonidov%40gmail.com/private-1b2dd71a5440e4cd42c7c7d4d77fd554/basic.ics'

# Nairobi time zone
NAIROBI_TZ = pytz.timezone('Africa/Nairobi')

def fetch_ical_events(ical_url):
    """Fetch and parse iCal events from the given URL"""
    response = requests.get(ical_url)
    response.raise_for_status()
    calendar = Calendar.from_ical(response.content)
    return [component for component in calendar.walk() if component.name == "VEVENT"]

def filter_today_events(events):
    """Filter events to include only today's events in Nairobi time zone"""
    today = datetime.datetime.now(NAIROBI_TZ).date()
    today_events = []
    for event in events:
        start = event.get('dtstart').dt
        end = event.get('dtend').dt
        if isinstance(start, datetime.datetime):
            start = start.astimezone(NAIROBI_TZ).date()
        if isinstance(end, datetime.datetime):
            end = end.astimezone(NAIROBI_TZ).date()
        if start <= today <= end:
            today_events.append(event)
    return today_events

@app.route('/events', methods=['GET'])
def get_events():
    try:
        events = fetch_ical_events(ICAL_URL)
        today_events = filter_today_events(events)
        logging.debug(f"Fetched today's events: {today_events}")
        return jsonify([{
            'summary': str(event.get('summary')),
            'start': event.get('dtstart').dt.astimezone(NAIROBI_TZ).isoformat() if isinstance(event.get('dtstart').dt, datetime.datetime) else event.get('dtstart').dt.isoformat(),
            'end': event.get('dtend').dt.astimezone(NAIROBI_TZ).isoformat() if isinstance(event.get('dtend').dt, datetime.datetime) else event.get('dtend').dt.isoformat()
        } for event in today_events])
    except Exception as error:
        logging.error(f"An error occurred: {error}")
        return jsonify({"error": str(error)}), 500

@app.route('/add_lesson', methods=['POST'])
def add_lesson():
    try:
        data = request.json
        student_name = data.get('student_name')
        lesson_description = data.get('description')
        lesson_date = data.get('date')
        lesson_subject = data.get('subject')
        # Add logic to create a lesson for the student
        logging.debug(f"Adding lesson for {student_name} with description {lesson_description} on {lesson_date} for subject {lesson_subject}")
        # For now, just return a success message
        return jsonify({"message": f"Lesson added for {student_name} with description {lesson_description} on {lesson_date} for subject {lesson_subject}"}), 200
    except Exception as error:
        logging.error(f"An error occurred while adding lesson: {error}")
        return jsonify({"error": str(error)}), 500

if __name__ == '__main__':
    app.run(debug=True)