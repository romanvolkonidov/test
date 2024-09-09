from flask import Flask, jsonify
from datetime import datetime, timezone, timedelta
from ics import Calendar
from io import StringIO
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Replace these with the iCAL URLs you want to fetch events from
ICAL_URLS = [
    'https://calendar.google.com/calendar/ical/romanvolkonidov%40gmail.com/private-1b2dd71a5440e4cd42c7c7d4d77fd554/basic.ics',
    'https://calendar.google.com/calendar/ical/violetta6520%40gmail.com/private-4668f11232a35223fb2b7f0224414ac9/basic.ics',
    'https://calendar.google.com/calendar/ical/violetta6520%40gmail.com/public/basic.ics',
    'https://calendar.google.com/calendar/ical/p8simije0nhss305jf5qak5sm0%40group.calendar.google.com/private-8471e32b9a066146ba0545efc6d5322d/basic.ics',
    'https://calendar.google.com/calendar/ical/o6bemnc7uc56hipv6t6lntccq4%40group.calendar.google.com/private-1f621ee25080da2111e7f1c5598322a9/basic.ics'
]

@app.route('/events', methods=['GET'])
def get_events():
    try:
        # Get the current time in the Africa/Nairobi timezone
        now = datetime.now(timezone(timedelta(hours=3)))
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        events = {}
        for ical_url in ICAL_URLS:
            response = requests.get(ical_url)
            calendar = Calendar(StringIO(response.text))

            for event in calendar.events:
                if event.begin.datetime >= start_time and event.end.datetime <= end_time:
                    event_summary = event.name
                    if event_summary not in events:
                        events[event_summary] = []
                    events[event_summary].append({
                        'summary': event.name,
                        'start': event.begin.datetime.isoformat(),
                        'end': event.end.datetime.isoformat()
                    })

        return jsonify(events)

    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': 'Error fetching events'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
