# This program updates the HISTORY_DATES config var

import datetime

# Only execute on Monday
if (datetime.datetime.today().weekday() == 0):
    import requests
    import os

    # Get date array from config var (format 'd1,d2,d3,d4' ) and convert to array
    # d1 is earliest, d4 is latest
    dateArr = os.environ['HISTORY_DATES']
    dateArr = dateArr.split(',')

    # Get date in YYYY-MM-DD format
    mondayDate = datetime.datetime.now().date() - datetime.timedelta(7)
    fridayDate = datetime.datetime.now().date() - datetime.timedelta(3)
    # Create date range
    dateRange = str(mondayDate) + "-" + str(fridayDate)

    # Add new date range to array
    dateArr.append(dateRange)

    # Delete oldest date from array
    del dateArr[0]

    #Build string to commit to variable
    newVar = ""
    for date in dateArr:
        newVar = newVar + date + ','
    newVar = newVar[:-1]

    # Change variable with Heroku API
    r = requests.patch("https://api.heroku.com/apps/sl-assignments/config-vars", data='{{"HISTORY_DATES":"{}"}}'.format(newVar), headers={"Content-Type": "application/json", "Accept": "application/vnd.heroku+json; version=3"})
    print(r)
    print(r.content)