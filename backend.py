"""TODO add Google Sheets compatability (add link on results, add loading wheel, add column headers)
TODO Verify scheduler works
TODO make history page:
- scheduler.py creates copy of table, saving date range to config variable
- render_template history.html
- by default, pass dates during render_template as a drop-down menu, then send jQuery with chosen one
- {% if result %} on history.html: display table with wanted range
- on success: display transparent "loading..." over table"""

from flask import Flask, jsonify, request, render_template
import json
import os
import psycopg2
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv

# Connect to database using heroku environment variable DATABASE_URL
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')# Heroku requires SSL

# Create a cursor to execute queries
cursor = conn.cursor()

def updateSheet():
    # Output data (currently a dict) to file so that you can use a python environment variable
    data = {
        "type": "service_account",
        "project_id": "assignmentssheet",
        "private_key_id": "821db85dfa53172a71eedcb3ab591699f2f3e693",
        "private_key": os.environ['DRIVE_PRIVATE_KEY'].replace('\\n', '\n'),
        "client_email": "sheeteditor@assignmentssheet.iam.gserviceaccount.com",
        "client_id": "107375601430696559484",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/sheeteditor%40assignmentssheet.iam.gserviceaccount.com"
    }
    # Convert dict to JSON string
    data = json.dumps(data, indent=2)

    # Don't need to change the file if it already exists
    if os.path.exists("assignmentssheet-821db85dfa53.json") == False:
        # Opening file automatically deletes contents and will create it if it doesn't exits
        outJSON = open("assignmentssheet-821db85dfa53.json", "w")
        outJSON.write(data)
        outJSON.close()

    # Connect to api service account
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('assignmentssheet-821db85dfa53.json', scope)
    client = gspread.authorize(creds)
    # Open sheet
    spreadsheet = client.open('SLSD Assignment Completion Database - Google Sheets')

    cursor.execute('SELECT * FROM assignments ORDER BY "ID" ASC')
    table = cursor.fetchall()

    #List comprehension to replace booleans with strings
    table = [[ "Completed" if cell==True else "Incomplete" if cell==False else cell for cell in row ] for row in table ]

    assignment_csv = open('sheet1.csv', 'w')
    csvWriter = csv.writer(assignment_csv, delimiter=',')
    csvWriter.writerow(["Student ID", "Last Name", "First Name", "Science", "Math", "English", "Social Studies", "World Language", "PE/Health/DE", "Special Education", "Music", "Art", "Family Consumer Science", "Technology Education", "Business", "Guidance Notes", "LCTI", "Supports", "Email"])
    csvWriter.writerows(table)
    # Close file so that it can update
    assignment_csv.close()


    assignment_csv = open('sheet1.csv', 'r')
    # Get content as a CSV string
    assignmentData = assignment_csv.read()
    client.import_csv(spreadsheet.id, assignmentData)
    assignment_csv.close()


# Initialize flask app
app = Flask(__name__)

# / and /index lead to same page
@app.route('/', methods=['GET', 'POST', 'GETPASSWORD'])

@app.route('/index', methods=['GET', 'POST', 'GETPASSWORD'])
def index():
    
    # On form submission:
    if request.method == "POST":
        # Get data from JSON string
        data = request.get_json()

        # Set the two part of the data, subject (string) and ids (list of strings)
        subject = data['subject']
        ids = data['ids']
        
        # Iterate through each id to update each applicable row
        for idNum in ids:
            # Use double quotes for case-sensitive variables
            query = 'UPDATE assignments SET "{}" = false WHERE "ID" = {}'.format(subject, idNum)
            cursor.execute(query)
        # Commit changes to the database
        conn.commit()

        updateSheet()

        # Return true (there was no error)
        return json.dumps(True)
    
    elif request.method == "GETPASSWORD":
        toPass = os.environ['PASS']
        return toPass

    elif request.method == "GET":
        # On page load, render index.html
        return render_template('index.html')

# Render submitted page after form submission
@app.route('/submitted')
def submitThanks():
    return render_template("submitted.html")

@app.route('/edit', methods=['GET', 'POST', 'GETPASSWORD'])
def edit():
    
    # On form submission:
    if request.method == "POST":
        # Get data from JSON string
        data = request.get_json()

        # Set the two part of the data, subject (string) and ids (list of strings)
        subject = data['subject']
        ids = data['ids']

        # Iterate through each id to update each applicable row
        for idNum in ids:
            # Use double quotes for case-sensitive variables
            query = 'UPDATE assignments SET "{}" = true WHERE "ID" = {}'.format(subject, idNum)
            cursor.execute(query)
        # Commit changes to the database
        conn.commit()

        updateSheet()

        # Return true (there was no error)
        return json.dumps(True)
    
    elif request.method == "GETPASSWORD":
        toPass = os.environ['PASS']
        return toPass

    elif request.method == "GET":
        # On page load, render edit.html
        return render_template('edit.html')

# Results page
@app.route('/results')
def view():
    # Get everything from database
    cursor.execute('SELECT * FROM assignments ORDER BY "ID" ASC')
    # Save each row as an element in a list
    passResult = cursor.fetchall()
    # Render results.html with result variable passed
    return render_template('results.html', result = passResult)

@app.route('/history', methods=['GET', 'VIEWHISTORY'])
def history():
    # Get dates and turn them into an array
    dates = os.environ['HISTORY_DATES']
    dates = dates.split(',')

    if request.method == 'VIEWHISTORY':
        data = request.get_json()
        dateIndex = data['dateRange']

        cursor.execute('SELECT * FROM "{}" ORDER BY "ID" ASC'.format(dateIndex))
        result = cursor.fetchall()

        return render_template('history.html', dates = dates, result = result)
    if request.method == 'GET':
        return render_template('history.html', dates = dates)

# Display about page
@app.route('/about')
def about():
    return render_template("about.html")

# Display emails
@app.route('/email')
def email():
    # Arrays to hold emails by number of incomplete
    one = []
    two = []
    three = []
    four = []
    five = []
    sixPlus = []

    # Counter for incomplete assignments
    incCount = 0

    # Get everything from database
    cursor.execute('SELECT * FROM assignments')
    # Save each row in list
    table = cursor.fetchall()
    for row in table:
        incCount = 0
        for i in range (3, (len(row)-1)):
            if row[i] == False:
                incCount += 1
        if (incCount == 1):
            one.append(row[len(row)-1])
        elif (incCount == 2):
            two.append(row[len(row)-1])
        elif (incCount == 3):
            three.append(row[len(row)-1])
        elif (incCount == 4):
            four.append(row[len(row)-1])
        elif (incCount == 5):
            five.append(row[len(row)-1])
        elif (incCount >= 6):
            sixPlus.append(row[len(row)-1])
        
        
    return render_template("email.html", oneArr = one, twoArr = two, threeArr = three, fourArr = four, fiveArr = five, sixArr = sixPlus)


# When program is run
if __name__ == '__main__':
    app.run()
    # Close cursor and connection once the program is done running
    cursor.close()
    conn.close()
