from __future__ import print_function
from fastapi import FastAPI
import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import dateutil.parser as parser
from pydantic import BaseModel

class meetingParameters(BaseModel):
    startDate: str
    endDate:str
    description: str
    location: str
    summary:str

# 2010-12-16T12:14:05+00:00
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly','https://www.googleapis.com/auth/calendar']
creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

def get_events():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """

    try:
        service = build('calendar', 'v3', credentials=creds)
        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return
        
        # Prints the start and name of the next 10 events
        all_events=dict()
        all_events["events"]=[]
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))

            all_events["events"].append({"start_Date":start, "Summary":event['summary'],"Descrtiption":event["description"],"location":event["location"],"Link":event["htmlLink"]})
            print(start, event['summary'])
        return all_events
    except HttpError as error:
        print('An error occurred: %s' % error)




def convertToISO(date):
    text = date
    date = parser.parse(text)
    date=date.isoformat()
    return date

def write_events(startDate,endDate,summary,description,location):
    print("StartDate :",startDate,"|EndDate :",endDate,"|Description :",description,"|summary :",summary,"|location :",location)
    event = {
    'summary': summary,
    'location': location,
    'description': description,
    'start': {
        'dateTime': convertToISO(startDate),
        'timeZone': 'America/Los_Angeles',
    },
    'end': {
        'dateTime': convertToISO(endDate),
        'timeZone': 'America/Los_Angeles',
    },
    'attendees': [
        {'email': 'pavan.kulkarni@kaleyra.com'},
    ],
    'reminders': {
        'useDefault': False,
        'overrides': [
        {'method': 'email', 'minutes': 24 * 60},
        {'method': 'popup', 'minutes': 10},
        ],
    },
    }
    try:
        service = build('calendar', 'v3', credentials=creds)
        # Call the Calendar API 
        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))
    except HttpError as err:
        print("Error :",err)

app = FastAPI()
@app.get('/getEvents')
def getEvents():
    response=get_events()
    return response

@app.get('/')
def welcome():
    return "Welcome to myAPI"

@app.post('/createEvents')
def createEvents(meetParameters:meetingParameters):
    startDate=meetParameters.startDate
    endDate=meetParameters.endDate
    description=meetParameters.description
    summary=meetParameters.summary
    location=meetParameters.location
    write_events(startDate,endDate,summary,description,location)
    return get_events()
 