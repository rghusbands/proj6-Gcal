#Proj8 MeetMe App
Meet Me application that uses multiple google calendars users and checks their free times to see when they can meet. Simply follow the instruction on the app!

ERRORS:
-can't seem to use the same browser
    -probably because uses cookies to know when different user
-make half screen addMember page not stuck to the wall
    -appears to be firefox issue(only when small window). Chrome doesn't    
     stick to the side.
-had problems using app with friend in texas. Denied connection.
-not designed for mobile

#Proj7
Obtain busy times from google calendar api and use them to display free times available for meetings.



#INSTRUCTIONS FOR PROJECT 6 (previous project)

# proj6-Gcal
Snarf appointment data from a selection of a user's Google calendars 

## What is here

I've provided code for the authorization (oauth2) protocol for Google
calendars.  There is also a picker for a date range. 

## What you'll add

You'll need to read the Google developer documentation to learn how to
obtain information from the Google Calendar service.

Your application should allow the user to choose calendars (a single
user may have several Google calendars, one of which is the 'primary'
calendar) and list 'blocking'  (non-transparent)
appointments between a start date and an end date
for some subset of them.

## Hints

You'll need a 'client secret' file of your own.  It should *not* be
under GIT control.  This is kind of a
developer key, which you need to obtain from Google.  See
https://auth0.com/docs/connections/social/google and
https://developers.google.com/identity/protocols/OAuth2 .
The applicable scenario for us is 'Web server applications'  (since
we're doing this in Flask).  

Your client secret will have to be registered for the URLs used for 
the oauth2 'callback' in the authorization protocol.  This URL includes
the port on which your application is running, so you you will need to 
use the same port each time you run your application.  I suggest you 
generate one random port in the range 5000-8000 and stick with it for the 
remainder of the term (unless someone else randomly draws the same port). 

More about the client secret file is described in our Piazza group. 

Whether or not you already have a Google calendar, it's a good idea to
create one or two 'test' calendars with a known set of appointments
for testing.



