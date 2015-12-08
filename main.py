import flask
from flask import render_template
from flask import request
from flask import url_for
import uuid

import json
import logging

# Date handling
import arrow # Replacement for datetime, based on moment.js
import datetime # But we still need time
from dateutil import tz  # For interpreting local times


# OAuth2  - Google library implementation for convenience
from oauth2client import client
import httplib2   # used in oauth2 flow

# Google API for services
from apiclient import discovery

# Mongo database
from pymongo import MongoClient
from bson.objectid import ObjectId

# random int for key
from random import randint

###
# Globals
###
import CONFIG
app = flask.Flask(__name__)


try:
    dbclient = MongoClient(CONFIG.MONGO_URL)
    db = dbclient.MeetMe
    collection = db.dated

except:
    print("Failure opening database. Is Mongo running? Correct password?")
    sys.exit(1)

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = CONFIG.GOOGLE_LICENSE_KEY  ## You'll need this
APPLICATION_NAME = 'MeetMe'


#############################
#
#  Pages (routed from URLs)
#
#############################

@app.route("/")
@app.route("/index")
def index():
  app.logger.debug("Entering index")
  if 'begin_date' not in flask.session:
    init_session_values()
  if 'calendars' in flask.session:
      flask.session.pop('calendars', None)
  return render_template('index.html')

@app.route("/choose")
def choose():
    ## We'll need authorization to list calendars
    ## I wanted to put what follows into a function, but had
    ## to pull it back here because the redirect has to be a
    ## 'return'
    app.logger.debug("Checking credentials for Google calendar access")
    credentials = valid_credentials()
    if not credentials:
      app.logger.debug("Redirecting to authorization")
      return flask.redirect(flask.url_for('oauth2callback'))
    global gcal_service #used in busyTimes
    gcal_service = get_gcal_service(credentials)
    app.logger.debug("Returned from get_gcal_service")
    flask.session['calendars'] = list_calendars(gcal_service)
    return render_template('index.html')

####
#
#  Google calendar authorization:
#      Returns us to the main /choose screen after inserting
#      the calendar_service object in the session state.  May
#      redirect to OAuth server first, and may take multiple
#      trips through the oauth2 callback function.
#
#  Protocol for use ON EACH REQUEST:
#     First, check for valid credentials
#     If we don't have valid credentials
#         Get credentials (jump to the oauth2 protocol)
#         (redirects back to /choose, this time with credentials)
#     If we do have valid credentials
#         Get the service object
#
#  The final result of successful authorization is a 'service'
#  object.  We use a 'service' object to actually retrieve data
#  from the Google services. Service objects are NOT serializable ---
#  we can't stash one in a cookie.  Instead, on each request we
#  get a fresh serivce object from our credentials, which are
#  serializable.
#
#  Note that after authorization we always redirect to /choose;
#  If this is unsatisfactory, we'll need a session variable to use
#  as a 'continuation' or 'return address' to use instead.
#
####

def valid_credentials():
    """
    Returns OAuth2 credentials if we have valid
    credentials in the session.  This is a 'truthy' value.
    Return None if we don't have credentials, or if they
    have expired or are otherwise invalid.  This is a 'falsy' value.
    """
    if 'credentials' not in flask.session:
      return None

    credentials = client.OAuth2Credentials.from_json(
        flask.session['credentials'])

    if (credentials.invalid or
        credentials.access_token_expired):
      return None
    return credentials


def get_gcal_service(credentials):
  """
  We need a Google calendar 'service' object to obtain
  list of calendars, busy times, etc.  This requires
  authorization. If authorization is already in effect,
  we'll just return with the authorization. Otherwise,
  control flow will be interrupted by authorization, and we'll
  end up redirected back to /choose *without a service object*.
  Then the second call will succeed without additional authorization.
  """
  app.logger.debug("Entering get_gcal_service")
  http_auth = credentials.authorize(httplib2.Http())
  service = discovery.build('calendar', 'v3', http=http_auth)
  app.logger.debug("Returning service")
  return service

@app.route('/oauth2callback')
def oauth2callback():
  """
  The 'flow' has this one place to call back to.  We'll enter here
  more than once as steps in the flow are completed, and need to keep
  track of how far we've gotten. The first time we'll do the first
  step, the second time we'll skip the first step and do the second,
  and so on.
  """
  app.logger.debug("Entering oauth2callback")
  flow =  client.flow_from_clientsecrets(
      CLIENT_SECRET_FILE,
      scope= SCOPES,
      redirect_uri=flask.url_for('oauth2callback', _external=True))
  ## Note we are *not* redirecting above.  We are noting *where*
  ## we will redirect to, which is this function.

  ## The *second* time we enter here, it's a callback
  ## with 'code' set in the URL parameter.  If we don't
  ## see that, it must be the first time through, so we
  ## need to do step 1.
  app.logger.debug("Got flow")
  if 'code' not in flask.request.args:
    app.logger.debug("Code not in flask.request.args")
    auth_uri = flow.step1_get_authorize_url()
    return flask.redirect(auth_uri)
    ## This will redirect back here, but the second time through
    ## we'll have the 'code' parameter set
  else:
    ## It's the second time through ... we can tell because
    ## we got the 'code' argument in the URL.
    app.logger.debug("Code was in flask.request.args")
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()
    ## Now I can build the service and execute the query,
    ## but for the moment I'll just log it and go back to
    ## the main screen
    app.logger.debug("Got credentials")
    return flask.redirect(flask.url_for('choose'))

#####
#
#  Option setting:  Buttons or forms that add some
#     information into session state.  Don't do the
#     computation here; use of the information might
#     depend on what other information we have.
#   Setting an option sends us back to the main display
#      page, where we may put the new information to use.
#
#####

#Add new members to the meet me app
#Seems to need to be a different browser
@app.route('/addMembers')
def addMember():
    key = request.args.get('key')
    flask.session['finalMeetingID'] = key
    return flask.redirect(flask.url_for("index"))


@app.route('/finalizeMeeting', methods=['POST'])
def finalizeMeeting():
    key = request.form.get('finalMeetingID')

    #checks to see if key can be turned into int
    try:
        int(key)
    except:
        flask.flash("Invalid Key")
        return flask.redirect(flask.url_for("index"))

    #if key is a number check valid number
    if (99999 < int(key) < 1000000):
        """valid key"""
    else:
        flask.flash("Invalid Key")
        return flask.redirect(flask.url_for("index"))

    #checks to see if id is even in database
    try:
        validate_key_count = 0
        for record in collection.find({"type":"date_range"}):
            if (record["id"] == key):
                validate_key_count+=1
            else:
                "not a match"
        if validate_key_count == 0:
            flask.flash("No matching keys in database")
            return flask.redirect(flask.url_for("index"))
        else:
            """there are matches in the collection"""
    except:
        flask.flash("No matching keys in database")
        return flask.redirect(flask.url_for("index"))

    start_end_tuple = mergeDateRanges(key)

    if (start_end_tuple == -1):
        flask.flash("No overlapping dates in date ranges between users")
        collection.remove({})
        return flask.redirect(flask.url_for("index"))

    start_date = start_end_tuple['start_date']
    end_date = start_end_tuple['end_date']

    all_events_list = getEvents(key)

    flask.session['final_proposal'] = 'true'

    free_times = freeTimes(all_events_list, start_date, end_date)
    print(start_date)
    print(type(start_date))
    print(end_date)
    print(type(end_date))
    print(free_times)
    displayFreeTimes(free_times)

    return flask.redirect(flask.url_for("index"))

@app.route('/deleteproposal', methods=['POST'])
def deleteproposal():
    #clears database of that proposal
    flask.session.pop('final_proposal', None)
    #ideally would only delete specific id number
    collection.remove({})
    return flask.redirect(flask.url_for("index"))

@app.route('/goback', methods=['POST'])
def goback():
    #goes back without clearing that database
    flask.session.pop('final_proposal', None)
    return flask.redirect(flask.url_for("index"))

@app.route('/setrange', methods=['POST'])
def setrange():

    """
    User chose a date range with the bootstrap daterange
    widget.
    """


    app.logger.debug("Entering setrange")
    flask.flash("Setrange gave us '{}'"
            .format(request.form.get('daterange')))
    daterange = request.form.get('daterange')
    flask.session['daterange'] = daterange
    daterange_parts = daterange.split()
    flask.session['begin_date'] = interpret_date(daterange_parts[0])
    flask.session['end_date'] = interpret_date(daterange_parts[2])
    key = str(randint(100000,999999))
    flask.session['meetingID'] = key
    try:
        key = flask.session['finalMeetingID']
        flask.session['meetingID'] = key
    except:
        """no final meeting id yet"""
    record = {"type": "date_range",
                    "id": key,
                    "start_date": flask.session['begin_date'],
                    "end_date": flask.session['end_date']
                    }
    collection.insert(record)
    app.logger.debug("Setrange parsed {} - {}  dates as {} - {}".format(
      daterange_parts[0], daterange_parts[1],
      flask.session['begin_date'], flask.session['end_date']))
    return flask.redirect(flask.url_for("choose"))

@app.route('/select_calendars', methods=['POST'])
def getCalendars():
    app.logger.debug("Get selected caldendars")
    selected_calendars = request.form.getlist('calendar')
    meetingID = str(flask.session['meetingID'])
    try:
        flask.session['finalMeetingID']
        flask.flash("Thanks for submitting. Please wait for proposer to get back to you!")
    except:
        flask.flash("This is the key to finalize below.")
        flask.flash(meetingID)
        flask.flash("Below is the url to provide to other meeting participants.")
        message = "ix.cs.uoregon.edu:6996/addMembers?key=" + meetingID
        flask.flash(message)

    full_calendars = []
    for cal in flask.session['calendars']:
        if cal['id'] in selected_calendars:
            full_calendars.append(cal)
    cal_event_list = calEventList(full_calendars)
    #put event times into one list
    for cal in cal_event_list:
        if cal: #In case list is empty
            for event in cal:
                #to local time below
                ev_start = arrow.get(event['start']).to('local')
                ev_end = arrow.get(event['end']).to('local')
                record = { "type":"busy_times",
                            "start": ev_start.isoformat(),
                            "end": ev_end.isoformat(),
                            "id": flask.session['meetingID']
                            }
                collection.insert(record)

    return flask.redirect(flask.url_for("index"))

####
#
#   Initialize session variables
#
####

def init_session_values():
    """
    Start with some reasonable defaults for date and time ranges.
    Note this must be run in app context ... can't call from main.
    """
    # Default date span = tomorrow to 1 week from now
    now = arrow.now('local')
    tomorrow = now.replace(days=+1)
    nextweek = now.replace(days=+7)
    flask.session["begin_date"] = tomorrow.floor('day').isoformat()
    flask.session["end_date"] = nextweek.ceil('day').isoformat()
    flask.session["daterange"] = "{} - {}".format(
        tomorrow.format("MM/DD/YYYY"),
        nextweek.format("MM/DD/YYYY"))
    # Default time span each day, 9 to 5
    flask.session["begin_time"] = interpret_time("9am")
    flask.session["end_time"] = interpret_time("5pm")

def interpret_time( text ):
    """
    Read time in a human-compatible format and
    interpret as ISO format with local timezone.
    May throw exception if time can't be interpreted. In that
    case it will also flash a message explaining accepted formats.
    """
    app.logger.debug("Decoding time '{}'".format(text))
    time_formats = ["ha", "h:mma",  "h:mm a", "H:mm"]
    try:
        as_arrow = arrow.get(text, time_formats).replace(tzinfo=tz.tzlocal())
        app.logger.debug("Succeeded interpreting time")
    except:
        app.logger.debug("Failed to interpret time")
        flask.flash("Time '{}' didn't match accepted formats 13:30 or 1:30pm"
              .format(text))
        raise
    return as_arrow.isoformat()

def interpret_date( text ):
    """
    Convert text of date to ISO format used internally,
    with the local time zone.
    """
    try:
      as_arrow = arrow.get(text, "MM/DD/YYYY").replace(
          tzinfo=tz.tzlocal())
    except:
        flask.flash("Date '{}' didn't fit expected format 12/31/2001")
        raise
    return as_arrow.isoformat()

def next_day(isotext):
    """
    ISO date + 1 day (used in query to Google calendar)
    """
    as_arrow = arrow.get(isotext)
    return as_arrow.replace(days=+1).isoformat()

####
#
#  Functions (NOT pages) that return some information
#
####

def getEvents(key):
    list = []
    for record in collection.find({"type": "busy_times"}):
        if (record['id'] == key):
            start = record['start']
            end = record['end']
            start = arrow.get(start)
            end = arrow.get(end)
            pair = {'start': start, 'end': end}
            list.append(pair)
    return list

def mergeDateRanges(key):
    starts = []
    ends = []
    for record in collection.find({"type":"date_range"}):
        if (record["id"] == key):
            start = record["start_date"]
            end = record["end_date"]
            starts.append(start)
            ends.append(end)
    starts.sort()
    ends.sort()
    start = starts[-1]
    end = ends[0]
    end = arrow.get(end).isoformat()
    if start <= end:
        return {'start_date': start, 'end_date': end}
    else:
        return -1

def freeTimes(all_events_list, start_date, end_date):

    #add nights as events
    all_events_list = addNights(all_events_list, start_date, end_date)
    sorted_events = sortEvents(all_events_list) #sort events
    free_times = getFreeTimes(sorted_events) #gets list of free times
    return free_times


def displayFreeTimes(free_times):
    #into a readable format for flask.flash
    for times in free_times:
        message = []
        message.append(readableDate(times[0]))
        message.append(" to ")
        message.append(readableDate(times[1]))
        message = ''.join(message)
        flask.flash(message)


def readableDate(date): #formats from arrow object to readable date
    return date.format('HH:mm MM/DD/YY')

def getFreeTimes(sorted_list):

    #gets rid of overlapping events
    improved_sorted_list = eliminateDuplicates(sorted_list)

    free_times = []
#Adds times from end of events to beginning of next events to free times list
    for i in range(len(improved_sorted_list)-1):
        event = improved_sorted_list[i]
        next_event = improved_sorted_list[i+1]
        if (event['end'] < next_event['start']):
            #put in an ordered list to ensure the same order
            free_times.append([event['end'], next_event['start']])
    return free_times


#gets rid of duplicate busy times
def eliminateDuplicates(list):
    new_list = []
    list_size = len(list)
    for i in range(list_size-1):
        event = list[i]
        next_event = list[i+1]
#If the next events start time is before the previous events end time then
#the previous events end time because the next events start time
        event['end'].replace
        if (event['end'] > next_event['start'] and event['end'] > next_event['end']):
            new_list.append({'start':event['start'], 'end':event['end']})
            list[i+1]['end'] = event['end'] #prevents problems with next iteration
        elif (event['end'] >= next_event['start']):
            new_list.append({'start':event['start'], 'end':next_event['start']})
        else:
            new_list.append({'start':event['start'], 'end':event['end']})
    #add last event to new_list
    new_list.append(list[list_size-1])
    return new_list


#add nights as events so free time is from 9am-5pm(normal work day)
def addNights(list, sd, ed):
    start_date = arrow.get(sd)
    #end_date = arrow.get(ed).replace(hours=-24)
    end_date = arrow.get(ed)
    for day in arrow.Arrow.span_range('day', start_date, end_date): #goes through day range
        early_morning = {'start':day[0], 'end':day[0].replace(hours=+9)}
        late_nights = {'start':day[1].replace(hours=-7).replace(seconds=+.000001), 'end':day[1].replace(seconds=+.000001)}
        list.append(early_morning)
        list.append(late_nights)
    return list


#returns sorted list of events based off start times
def sortEvents(list):
    start_times = []
    #puts all the starts in a list
    for ev in list: #ev is event
        start_times.append(ev['start'])
    #sorts start times
    start_times.sort()
    sorted_times = []
    #puts ordered start times with the respective end times
    for times in start_times:
        for ev in list:
            if (times == ev['start']):
                sorted_times.append({'start':ev['start'], 'end':ev['end']})
    return sorted_times


#gets list of events based off selected calendars
def calEventList(cal_list):
    begin_date = flask.session['begin_date'] #gets user inputed start date
    end_date = flask.session['end_date'] #gets user inputed end date
    end_date = arrow.get(end_date).replace(hours=+24).isoformat() #add 24 hours to include whole day
    #flask.session['end_date'] = end_date
    busy_times = []
    for cal in cal_list:
        calID = cal['id']
        freebusy_query = {
            "timeMin" : begin_date,
            "timeMax" : end_date,
            "items" : [{ "id" : calID }]
        }
        result = gcal_service.freebusy().query(body=freebusy_query).execute()
        result_times = result['calendars'][calID]['busy']
        busy_times.append(result_times)
    return busy_times


def list_calendars(service):
    """
    Given a google 'service' object, return a list of
    calendars.  Each calendar is represented by a dict, so that
    it can be stored in the session object and converted to
    json for cookies. The returned list is sorted to have
    the primary calendar first, and selected (that is, displayed in
    Google Calendars web app) calendars before unselected calendars.
    """
    app.logger.debug("Entering list_calendars")
    calendar_list = service.calendarList().list().execute()["items"]
    result = []
    for cal in calendar_list:
        kind = cal["kind"]
        id = cal["id"]
        if "description" in cal:
            desc = cal["description"]
        else:
            desc = "(no description)"
        summary = cal["summary"]
        # Optional binary attributes with False as default
        selected = ("selected" in cal) and cal["selected"]
        primary = ("primary" in cal) and cal["primary"]


        result.append(
          { "kind": kind,
            "id": id,
            "summary": summary,
            "selected": selected,
            "primary": primary
            })
    return sorted(result, key=cal_sort_key)


def cal_sort_key( cal ):
    """
    Sort key for the list of calendars:  primary calendar first,
    then other selected calendars, then unselected calendars.
    (" " sorts before "X", and tuples are compared piecewise)
    """
    if cal["selected"]:
       selected_key = " "
    else:
       selected_key = "X"
    if cal["primary"]:
       primary_key = " "
    else:
       primary_key = "X"
    return (primary_key, selected_key, cal["summary"])


#################
#
# Functions used within the templates
#
#################

@app.template_filter( 'fmtdate' )
def format_arrow_date( date ):
    try:
        normal = arrow.get( date )
        return normal.format("ddd MM/DD/YYYY")
    except:
        return "(bad date)"

@app.template_filter( 'fmttime' )
def format_arrow_time( time ):
    try:
        normal = arrow.get( time )
        return normal.format("HH:mm")
    except:
        return "(bad time)"

#############


if __name__ == "__main__":
  # App is created above so that it will
  # exist whether this is 'main' or not
  # (e.g., if we are running in a CGI script)

  app.secret_key = str(uuid.uuid4())
  app.debug=CONFIG.DEBUG
  app.logger.setLevel(logging.DEBUG)
  # We run on localhost only if debugging,
  # otherwise accessible to world
  if CONFIG.DEBUG:
    # Reachable only from the same computer
    app.run(port=CONFIG.PORT)
  else:
    # Reachable from anywhere
    app.run(port=CONFIG.PORT,host="0.0.0.0")

