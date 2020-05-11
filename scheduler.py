# This program updates the PostgreSQL db
import datetime

# Only execute on Monday
if (datetime.datetime.today().weekday() == 0):
    import os
    import json
    import psycopg2
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    import csv
    from backend import updateSheet

    # Connect to db
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')

    cursor = conn.cursor()

    # Get date array from config var (format 'd1,d2,d3,d4' ) and convert to array
    # d1 is earliest, d4 is latest
    dateArr = os.environ['HISTORY_DATES']
    dateArr = dateArr.split(',')

    # Shift over dates 0<-1 1<-2 2<-3 + 3
    for i in range(len(dateArr)):
        cursor.execute('DELETE FROM "{}"'.format(i))
        if i != (len(dateArr)-1):
            cursor.execute('INSERT INTO "{}" SELECT * FROM "{}"'.format(i, (i+1)))
        else:
            cursor.execute('INSERT INTO "{}" SELECT * FROM assignments'.format(i))
    conn.commit()  

    subject_arr = ["Science", "Math", "English", "Social Studies", "World Language", "PE/Health/DE", "Special Education", "Music", "Art", "Family Consumer Science", "Technology Education", "Business", "Guidance Notes", "LCTI", "Supports"]
    # Iterate through each subject (column), setting all rows to true
    for subject in subject_arr:
        cursor.execute('UPDATE assignments SET "{}" = true'.format(subject))

    # Commit changes
    conn.commit()
    
    updateSheet()
    
    #Close cursor and connection
    cursor.close()
    conn.close()